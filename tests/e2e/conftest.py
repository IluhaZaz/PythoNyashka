import json
import os
import shutil
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import httpx
import pytest

COMPOSE_FILE = Path(__file__).with_name("compose.yaml")


@dataclass(frozen=True)
class Stand:
    client: httpx.Client
    compose: list[str]
    env: dict[str, str]

    def inbox(self) -> list[dict]:
        result = subprocess.run(
            [
                *self.compose,
                "exec",
                "-T",
                "bff",
                "python",
                "-c",
                "from urllib.request import urlopen; "
                "print(urlopen('http://mailpit:8025/api/v1/messages', timeout=3).read().decode())",
            ],
            env=self.env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
            timeout=10,
        )
        return json.loads(result.stdout)["messages"] or []


def make_certificate(directory: Path) -> None:
    openssl = shutil.which("openssl")
    if openssl is None and os.name == "nt":
        bundled = Path(os.environ.get("ProgramFiles", "C:/Program Files"))
        candidate = bundled / "Git" / "usr" / "bin" / "openssl.exe"
        if candidate.is_file():
            openssl = str(candidate)
    if openssl is None:
        pytest.fail("OpenSSL is required to generate the temporary SMTP certificate")
    config = directory / "openssl.cnf"
    config.write_text(
        "[req]\ndistinguished_name = dn\nprompt = no\nx509_extensions = tls\n"
        "[dn]\nCN = mailpit\n[tls]\nsubjectAltName = DNS:mailpit\n",
        encoding="ascii",
    )
    certificate = subprocess.run(
        [
            openssl,
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-nodes",
            "-days",
            "2",
            "-config",
            "openssl.cnf",
            "-keyout",
            "key.pem",
            "-out",
            "cert.pem",
        ],
        cwd=directory,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert certificate.returncode == 0, certificate.stderr
    (directory / "key.pem").chmod(0o644)


@pytest.fixture(scope="session")
def stand(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Stand]:
    directory = tmp_path_factory.mktemp("smtp")
    make_certificate(directory)
    env_file = directory / "compose.env"
    env_file.touch()
    project = f"pythonyashka-e2e-{uuid4().hex[:10]}"
    env = {**os.environ, "E2E_CERT_DIR": directory.as_posix()}
    compose = [
        "docker",
        "compose",
        "--project-name",
        project,
        "--env-file",
        str(env_file),
        "-f",
        str(COMPOSE_FILE),
    ]

    def run(*args: str, timeout: int = 60, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(
            [*compose, *args],
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=check,
        )

    built = False
    try:
        try:
            run("build", "migrations", timeout=600)
        except subprocess.CalledProcessError as exc:
            details = (exc.stdout + "\n" + exc.stderr).strip()
            pytest.fail(f"E2E image build failed:\n{details[-4000:]}", pytrace=False)
        built = True
        try:
            run("up", "--no-build", "--wait", "--wait-timeout", "150", timeout=420)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            logs = run("logs", "--no-color", "--tail", "20", check=False)
            print(logs.stdout)
            raise
        address = run("port", "bff", "8000").stdout.strip()
        with httpx.Client(base_url=f"http://{address}", trust_env=False, timeout=10) as client:
            yield Stand(client, compose, env)
    finally:
        try:
            run("down", "--volumes", "--remove-orphans")
        finally:
            if built:
                subprocess.run(
                    ["docker", "image", "rm", f"{project}-app"],
                    env=env,
                    capture_output=True,
                    check=True,
                    timeout=60,
                )
