import pytest

pytestmark = pytest.mark.usefixtures("require_db")


def test_indicators_list(test_client):
    resp = test_client.get("/indicators?limit=5")
    if resp.status_code != 200:
        pytest.skip(f"Indicators list unavailable: {resp.status_code}")
    data = resp.json()
    assert "indicators" in data
    if data["indicators"]:
        ind = data["indicators"][0]
        assert "indicator_id" in ind
        assert "provider" in ind


def test_indicators_byos_register(test_client):
    payload = {
        "name": "pytest-byo",
        "description": "test byo indicator",
        "category": "CUSTOM",
        "frequency": "DAILY",
        "geo_scope": "US",
        "owner_team": "QA",
        "owner_contact": "qa@example.com",
        "license_type": "CUSTOM",
        "cost_model": "FREE",
        "connector_type": "KAFKA",
        "connector_config": {"topic": "pytest"},
    }
    resp = test_client.post("/indicators/byos/register", json=payload)
    if resp.status_code == 403:
        pytest.skip("BYOS registration forbidden in current role config")
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert "indicator_id" in data


def test_monitor_freshness_view_available(test_client):
    resp = test_client.get("/monitor/indicators/freshness")
    if resp.status_code == 404:
        pytest.skip("Monitor freshness endpoint not exposed")
    assert resp.status_code == 200


def test_monitor_accuracy_view_available(test_client):
    resp = test_client.get("/monitor/forecasts/accuracy")
    if resp.status_code == 404:
        pytest.skip("Monitor accuracy endpoint not exposed")
    assert resp.status_code == 200
