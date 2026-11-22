import json
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.security


@pytest.fixture(scope="module")
def production_compose():
    if shutil.which("docker") is None:
        pytest.skip("Docker Compose is required to validate the production topology")
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [
            "docker",
            "compose",
            "--env-file",
            ".docker/.env.prod",
            "-f",
            ".docker/docker-compose-prod.yaml",
            "config",
            "--no-env-resolution",
            "--no-interpolate",
            "--format",
            "json",
        ],
        cwd=root,
        capture_output=True,
        encoding="utf-8",
        timeout=20,
        check=True,
    )
    return json.loads(result.stdout)


def test_only_bff_publishes_host_ports(production_compose):
    services = production_compose["services"]
    assert {name for name, service in services.items() if service.get("ports")} == {"bff"}
    assert all(service.get("network_mode") != "host" for service in services.values())


def test_internal_services_use_only_the_internal_network(production_compose):
    networks = production_compose["networks"]
    assert networks["backend"]["internal"] is True
    for name, service in production_compose["services"].items():
        if name != "bff":
            assert set(service["networks"]) == {"backend"}, name
