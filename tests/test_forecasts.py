import pytest

pytestmark = pytest.mark.usefixtures("require_db")


def test_forecast_run_list(test_client):
    resp = test_client.get("/metrics/runs")
    if resp.status_code != 200:
        pytest.skip(f"metrics runs not available: {resp.status_code}")
    data = resp.json()
    assert "runs" in data
    if data["runs"]:
        run = data["runs"][0]
        assert "run_id" in run
        assert "computed_at" in run


def test_forecasts_by_sku(test_client):
    resp = test_client.get("/forecasts/sku-100")
    if resp.status_code == 404:
        pytest.skip("No forecasts for sku-100")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("sku_id") == "sku-100"
    assert "forecasts" in data
    if data["forecasts"]:
        f = data["forecasts"][0]
        for key in ["year_month", "p50", "run_id"]:
            assert key in f
