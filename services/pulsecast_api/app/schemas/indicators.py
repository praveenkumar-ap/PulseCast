from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class IndicatorCatalogSchema(BaseModel):
    indicator_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    frequency: Optional[str] = None
    provider: Optional[str] = None
    owner_team: Optional[str] = None
    owner_contact: Optional[str] = None
    geo_scope: Optional[str] = None
    unit: Optional[str] = None
    is_leading_indicator: Optional[bool] = None
    default_lead_months: Optional[float] = None
    sla_freshness_hours: Optional[int] = None
    sla_coverage_notes: Optional[str] = None
    license_type: Optional[str] = None
    cost_model: Optional[str] = None
    cost_estimate_per_month: Optional[float] = None
    status: Optional[str] = None
    is_external: Optional[bool] = None
    is_byo: Optional[bool] = None
    tags: Optional[str] = None
    connector_type: Optional[str] = None
    connector_config: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class IndicatorQualitySchema(BaseModel):
    indicator_id: str
    metric_date: Optional[datetime] = None
    correlation_score: Optional[float] = None
    correlation_stability_score: Optional[float] = None
    importance_score: Optional[float] = None
    causality_score: Optional[float] = None
    data_completeness_pct: Optional[float] = None
    lead_quality_score: Optional[float] = None
    last_correlation_range: Optional[str] = None
    last_eval_at: Optional[datetime] = None
    is_recommended: Optional[bool] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class IndicatorFreshnessSchema(BaseModel):
    indicator_id: str
    snapshot_time: Optional[datetime] = None
    last_data_time: Optional[datetime] = None
    lag_hours: Optional[float] = None
    is_within_sla: Optional[bool] = None
    miss_count: Optional[float] = None
    late_count: Optional[float] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class IndicatorTrustScore(BaseModel):
    indicator_id: str
    trust_score: Optional[float] = None
    lead_quality_score: Optional[float] = None
    stability_component: Optional[float] = None
    freshness_component: Optional[float] = None
    correlation_score: Optional[float] = None
    correlation_stability_score: Optional[float] = None
    importance_score: Optional[float] = None
    causality_score: Optional[float] = None
    data_completeness_pct: Optional[float] = None
    last_correlation_range: Optional[str] = None
    last_eval_at: Optional[datetime] = None
    is_recommended: Optional[bool] = None
    notes: Optional[str] = None
    snapshot_time: Optional[datetime] = None
    last_data_time: Optional[datetime] = None
    lag_hours: Optional[float] = None
    is_within_sla: Optional[bool] = None
    miss_count: Optional[float] = None
    late_count: Optional[float] = None

    class Config:
        from_attributes = True


class IndicatorDetail(BaseModel):
    catalog: IndicatorCatalogSchema
    quality: Optional[IndicatorQualitySchema] = None
    freshness: Optional[IndicatorFreshnessSchema] = None


class IndicatorSummary(BaseModel):
    indicator_id: str
    name: Optional[str] = None
    category: Optional[str] = None
    provider: Optional[str] = None
    status: Optional[str] = None
    is_byo: Optional[bool] = None
    tags: Optional[str] = None
    trust_score: Optional[float] = None


class IndicatorListResponse(BaseModel):
    indicators: List[IndicatorSummary]


class CreateIndicatorRequest(BaseModel):
    indicator_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    frequency: Optional[str] = None
    provider: Optional[str] = None
    owner_team: Optional[str] = None
    owner_contact: Optional[str] = None
    geo_scope: Optional[str] = None
    unit: Optional[str] = None
    is_leading_indicator: Optional[bool] = None
    default_lead_months: Optional[float] = None
    sla_freshness_hours: Optional[int] = None
    sla_coverage_notes: Optional[str] = None
    license_type: Optional[str] = None
    cost_model: Optional[str] = None
    cost_estimate_per_month: Optional[float] = None
    status: Optional[str] = "ACTIVE"
    is_external: Optional[bool] = True
    is_byo: Optional[bool] = False
    tags: Optional[str] = None
    connector_type: Optional[str] = None
    connector_config: Optional[str] = None


class UpdateIndicatorRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    frequency: Optional[str] = None
    provider: Optional[str] = None
    owner_team: Optional[str] = None
    owner_contact: Optional[str] = None
    geo_scope: Optional[str] = None
    unit: Optional[str] = None
    is_leading_indicator: Optional[bool] = None
    default_lead_months: Optional[float] = None
    sla_freshness_hours: Optional[int] = None
    sla_coverage_notes: Optional[str] = None
    license_type: Optional[str] = None
    cost_model: Optional[str] = None
    cost_estimate_per_month: Optional[float] = None
    status: Optional[str] = None
    is_external: Optional[bool] = None
    is_byo: Optional[bool] = None
    tags: Optional[str] = None
    connector_type: Optional[str] = None
    connector_config: Optional[str] = None


class UpdateQualityRequest(BaseModel):
    metric_date: Optional[datetime] = None
    correlation_score: Optional[float] = None
    correlation_stability_score: Optional[float] = None
    importance_score: Optional[float] = None
    causality_score: Optional[float] = None
    data_completeness_pct: Optional[float] = None
    lead_quality_score: Optional[float] = None
    last_correlation_range: Optional[str] = None
    last_eval_at: Optional[datetime] = None
    is_recommended: Optional[bool] = None
    notes: Optional[str] = None


class UpdateFreshnessRequest(BaseModel):
    snapshot_time: Optional[datetime] = None
    last_data_time: Optional[datetime] = None
    lag_hours: Optional[float] = None
    is_within_sla: Optional[bool] = None
    miss_count: Optional[float] = None
    late_count: Optional[float] = None


class ByosRegisterRequest(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    frequency: str
    geo_scope: Optional[str] = None
    owner_team: str
    owner_contact: str
    license_type: str
    cost_model: str
    cost_estimate_per_month: Optional[float] = None
    connector_type: str
    connector_config: Optional[dict] = None
    provider: Optional[str] = "CUSTOM"
    unit: Optional[str] = None
    tags: Optional[str] = None
    is_leading_indicator: Optional[bool] = None
    default_lead_months: Optional[float] = None
    sla_freshness_hours: Optional[int] = None
    sla_coverage_notes: Optional[str] = None
    status: Optional[str] = None


class IndicatorDetailResponse(BaseModel):
    indicator: IndicatorDetail


class IndicatorTrustScoresResponse(BaseModel):
    scores: List[IndicatorTrustScore]


class IndicatorTrustScoreResponse(BaseModel):
    score: IndicatorTrustScore
