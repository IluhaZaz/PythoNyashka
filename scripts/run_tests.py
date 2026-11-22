import argparse
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from tempfile import mkdtemp
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"

MODULES = {
    "auth": [
        "tests/services/test_auth_api.py",
        "tests/workers/test_kafka.py::test_notification_publisher_handles_broker_error",
        "tests/workers/test_lifespan.py::test_auth_lifespan_starts_producer_and_disposes_resources",
    ],
    "bff": ["tests/bff"],
    "chat": ["tests/services/test_chat_api.py"],
    "match": ["tests/services/test_match_api.py"],
    "media": ["tests/services/test_media_api.py"],
    "notification": [
        "tests/services/test_notification_api.py",
        "tests/services/test_notification_worker.py",
        "tests/workers/test_kafka.py",
        "tests/workers/test_smtp.py",
        "tests/workers/test_lifespan.py::test_notification_lifespan_cancels_worker_before_stopping_consumer",
    ],
    "profile": ["tests/services/test_profile_api.py"],
    "security": ["-m", "security"],
    "backend": [],
    "e2e": ["tests/e2e", "-m", "e2e"],
}


def run_job(name: str, report_dir: Path) -> int:
    xml = report_dir / f"{name}.xml"
    if name == "frontend":
        command = [
            "node",
            "node_modules/vitest/vitest.mjs",
            "run",
            "--reporter=default",
            "--reporter=junit",
            f"--outputFile.junit={xml}",
        ]
        cwd = FRONTEND
    else:
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-rxX",
            f"--junitxml={xml}",
            *MODULES[name],
        ]
        cwd = ROOT

    log = report_dir / f"{name}.log"
    print(f"\n=== {name} ===", flush=True)
    with log.open("w", encoding="utf-8") as output:
        try:
            with subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                errors="replace",
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            ) as process:
                for line in process.stdout:
                    output.write(line)
                    print(line, end="", flush=True)
                return process.wait()
        except OSError as error:
            message = f"Could not start {name}: {error}"
            output.write(message + "\n")
            print(message, file=sys.stderr)
            return 1


def read_results(xml: Path) -> list[tuple[str, str, str]]:
    results = []
    for case in ElementTree.parse(xml).iter("testcase"):
        name = "::".join(filter(None, (case.get("classname"), case.get("name"))))
        for tag, status in (("failure", "FAIL"), ("error", "ERROR"), ("skipped", "SKIP")):
            result = case.find(tag)
            if result is not None:
                if result.get("type") == "pytest.xfail":
                    status = "XFAIL"
                results.append((status, name, result.get("message", "")))
                break
        else:
            results.append(("PASS", name, ""))
    return results


def main() -> int:
    sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="Run a test suite and save results.")
    parser.add_argument("suite", choices=[*MODULES, "frontend", "regression"])
    parser.add_argument("--report-dir", type=Path, default=ROOT / "test-reports")
    args = parser.parse_args()
    args.report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    directory = Path(mkdtemp(prefix=f"{timestamp}-{args.suite}-", dir=args.report_dir.resolve()))
    jobs = ("backend", "frontend", "e2e") if args.suite == "regression" else (args.suite,)
    summary = directory / "summary.txt"
    success = True

    with summary.open("w", encoding="utf-8") as report:
        report.write(f"Suite: {args.suite}\n")
        for job in jobs:
            code = run_job(job, directory)
            report.write(f"\n[{job}] Runner exit code: {code}\nLog: {job}.log\n")
            try:
                results = read_results(directory / f"{job}.xml")
            except (OSError, ElementTree.ParseError) as error:
                report.write(f"ERROR: JUnit report unavailable: {error}\n")
                success = False
                report.flush()
                continue
            counts = Counter(status for status, _, _ in results)
            report.write(
                ", ".join(f"{status}: {count}" for status, count in sorted(counts.items()))
            )
            report.write(f"\nJUnit: {job}.xml\n\n")
            for status, name, message in results:
                reason = f" — {message}" if message else ""
                report.write(f"{status:5} {name}{reason}\n")
            if not results:
                report.write("ERROR: No test cases in the JUnit report\n")
            if code != 0 or not results or counts["FAIL"] or counts["ERROR"]:
                success = False
            report.flush()
        report.write(f"\nResult: {'PASS' if success else 'FAIL'}\n")
    print(f"\nReport: {summary}")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
