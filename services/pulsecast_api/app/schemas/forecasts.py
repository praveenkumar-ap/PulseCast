from typing import List, Optional

from pydantic import BaseModel


class ForecastItem(BaseModel):
    year_month: str
    p10: Optional[float] = None
    p50: Optional[float] = None
    p90: Optional[float] = None
    run_id: str


class ForecastResponse(BaseModel):
    sku_id: str
    forecasts: List[ForecastItem]
