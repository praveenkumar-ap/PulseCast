from typing import List, Optional

from pydantic import BaseModel


class ForecastItem(BaseModel):
    """Forecast entry for a given month."""

    year_month: str
    p10: Optional[float] = None
    p50: Optional[float] = None
    p90: Optional[float] = None
    run_id: str


class ForecastResponse(BaseModel):
    """Forecast response envelope per SKU."""

    sku_id: str
    forecasts: List[ForecastItem]
