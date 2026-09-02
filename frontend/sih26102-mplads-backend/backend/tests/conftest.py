import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]
TEST_DATABASE = BACKEND_ROOT / "test-mplads.db"
sys.path.insert(0, str(BACKEND_ROOT))
os.environ["MPLADS_DATABASE_URL"] = f"sqlite:///{TEST_DATABASE.as_posix()}"
os.environ["MPLADS_AUTH_ENABLED"] = "false"
os.environ["MPLADS_SEED_DEMO_DATA"] = "true"

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    if TEST_DATABASE.exists():
        TEST_DATABASE.unlink()
    with TestClient(app) as test_client:
        yield test_client
    if TEST_DATABASE.exists():
        TEST_DATABASE.unlink()

