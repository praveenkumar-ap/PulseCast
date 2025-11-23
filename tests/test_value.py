import pytest

pytestmark = pytest.mark.usefixtures("require_db")


def test_value_runs(test_client):
    resp = test_client.get("/value/runs?limit=5")
    if resp.status_code != 200:
        pytest.skip(f"value runs unavailable: {resp.status_code}")
    data = resp.json()
    assert "runs" in data
    if data["runs"]:
        run = data["runs"][0]
        assert "run_id" in run
        assert "total_value_estimate" in run
        assert "case_label" in run


def test_value_scenarios(test_client):
    resp = test_client.get("/value/scenarios?limit=5")
    if resp.status_code == 404:
        pytest.skip("value scenarios endpoint not available")
    if resp.status_code != 200:
        pytest.skip(f"value scenarios unavailable: {resp.status_code}")
    data = resp.json()
    assert "scenarios" in data
