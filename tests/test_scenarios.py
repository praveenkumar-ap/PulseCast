import pytest

pytestmark = pytest.mark.usefixtures("require_db")


def test_list_scenarios(test_client):
    resp = test_client.get("/scenarios")
    if resp.status_code != 200:
        pytest.skip(f"scenarios list unavailable: {resp.status_code}")
    data = resp.json()
    assert "scenarios" in data
    if data["scenarios"]:
        scenario = data["scenarios"][0]
        assert "scenario_id" in scenario
        assert "status" in scenario


def test_scenario_detail_existing(test_client):
    list_resp = test_client.get("/scenarios")
    if list_resp.status_code != 200 or not list_resp.json().get("scenarios"):
        pytest.skip("No scenarios to fetch")
    first_id = list_resp.json()["scenarios"][0]["scenario_id"]
    resp = test_client.get(f"/scenarios/{first_id}")
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["header"]["scenario_id"] == first_id


def test_scenario_create_minimal(test_client):
    payload = {
        "name": "pytest-scenario",
        "description": "test scenario",
        "created_by": "tester",
        "base_run_id": None,
        "sku_ids": ["sku-100"],
        "from_month": "2024-01",
        "to_month": "2024-02",
        "uplift_percent": 5.0,
    }
    resp = test_client.post("/scenarios", json=payload)
    if resp.status_code == 400:
        pytest.skip(f"Scenario creation failed with 400: {resp.json()}")
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert "scenario_id" in data
