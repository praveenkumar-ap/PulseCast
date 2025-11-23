import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure app package importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)


# Force test-friendly env (override any inherited values)
os.environ["ENVIRONMENT"] = "local"
os.environ["AUTH_MODE"] = "none"
os.environ["LOG_LEVEL"] = "INFO"
# Make sure roles include ADMIN so require_roles passes
os.environ["ALLOWED_ROLES"] = "PLANNER,SOP_APPROVER,DATA_SCIENTIST,ADMIN,SUPPORT_OPERATOR"

from services.pulsecast_api.app.main import create_app  # noqa: E402
from services.pulsecast_api.app.core.db import SessionLocal  # noqa: E402


@pytest.fixture(scope="session")
def test_client():
    app = create_app()
    return TestClient(app)


@pytest.fixture(scope="session")
def db_available():
    try:
        session = SessionLocal()
        session.execute("select 1")
        session.close()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def require_db(db_available):
    if not db_available:
        pytest.skip("Database not available for tests")
