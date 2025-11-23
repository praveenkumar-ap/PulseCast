import pytest

pytestmark = pytest.mark.usefixtures("require_db")


def test_healthz(test_client):
    resp = test_client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"
    assert "env" in data


@pytest.mark.usefixtures("db_available")
def test_readyz(test_client, db_available):
    resp = test_client.get("/readyz")
    if not db_available and resp.status_code == 503:
        pytest.skip("DB not available for readiness check")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ready"
    assert data.get("checks", {}).get("db") == "ok"
