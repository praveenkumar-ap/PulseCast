import pytest

pytestmark = pytest.mark.usefixtures("require_db")


def test_optimizer_listing_or_run(test_client):
    # Try listing recommendations if such endpoint exists
    resp = test_client.get("/optimizer/recommendations")
    if resp.status_code == 404:
        # fallback: try run endpoint if exists
        payload = {"sku_ids": ["sku-100"], "from_month": "2024-01", "to_month": "2024-02"}
        resp = test_client.post("/optimizer/run", json=payload)
    if resp.status_code == 404:
        pytest.skip("Optimizer endpoints not available")
    assert resp.status_code in (200, 201)
