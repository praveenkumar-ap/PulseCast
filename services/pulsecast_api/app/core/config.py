import os
from typing import List, Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = SettingsConfigDict(case_sensitive=False, env_ignore={"allowed_roles"})

    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(default="pulsecast", env="DB_NAME")
    db_user: str = Field(default="pulsecast", env="DB_USER")
    db_password: str = Field(default="pulsecast", env="DB_PASSWORD")
    app_env: str = Field(default="dev", env="APP_ENV")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    llm_provider: str = Field(default="none", env="LLM_PROVIDER")
    llm_model_name: Optional[str] = Field(default=None, env="LLM_MODEL_NAME")
    llm_api_key: Optional[str] = Field(default=None, env="LLM_API_KEY")
    llm_endpoint: Optional[str] = Field(default=None, env="LLM_ENDPOINT")
    llm_api_version: Optional[str] = Field(default=None, env="LLM_API_VERSION")
    llm_max_tokens: int = Field(default=512, env="LLM_MAX_TOKENS")
    llm_temperature: float = Field(default=0.2, env="LLM_TEMPERATURE")
    stream_provider: str = Field(default="none", env="STREAM_PROVIDER")
    stream_signals_topic: Optional[str] = Field(default=None, env="STREAM_SIGNALS_TOPIC")
    stream_group_id_signals_consumer: Optional[str] = Field(default=None, env="STREAM_GROUP_ID_SIGNALS_CONSUMER")
    kafka_bootstrap_servers: Optional[str] = Field(default=None, env="KAFKA_BOOTSTRAP_SERVERS")
    stream_poll_interval_ms: int = Field(default=1000, env="STREAM_POLL_INTERVAL_MS")
    stream_max_batch_size: int = Field(default=100, env="STREAM_MAX_BATCH_SIZE")
    stream_spike_delta_pct_threshold: float = Field(default=0.5, env="STREAM_SPIKE_DELTA_PCT_THRESHOLD")
    fluview_base_url: str = Field(default="https://api.delphi.cmu.edu/epidata/fluview/", env="FLUVIEW_BASE_URL")
    fluview_regions: List[str] = Field(default_factory=lambda: ["nat"], env="FLUVIEW_REGIONS")
    fluview_epiweek_start: Optional[str] = Field(default=None, env="FLUVIEW_EPIWEEK_START")
    fluview_epiweek_end: Optional[str] = Field(default=None, env="FLUVIEW_EPIWEEK_END")
    open_meteo_base_url: str = Field(default="https://archive-api.open-meteo.com/v1/archive", env="OPEN_METEO_BASE_URL")
    open_meteo_locations: List[dict] = Field(
        default_factory=lambda: [
            {"label": "us_northeast", "lat": 43.0, "lon": -75.0},
            {"label": "us_south", "lat": 31.0, "lon": -84.0},
        ],
        env="OPEN_METEO_LOCATIONS",
    )
    weather_start_date: Optional[str] = Field(default=None, env="WEATHER_START_DATE")
    weather_end_date: Optional[str] = Field(default=None, env="WEATHER_END_DATE")
    replay_speed_factor: float = Field(default=1.0, env="REPLAY_SPEED_FACTOR")
    replay_sleep_seconds: float = Field(default=0.5, env="REPLAY_SLEEP_SECONDS")
    environment: str = Field(default="dev", env="ENVIRONMENT")  # local | dev | staging | prod
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    auth_mode: str = Field(default="none", env="AUTH_MODE")  # none | dev_header | jwt/oidc placeholder
    allowed_roles_raw: str = Field(default="PLANNER,SOP_APPROVER,DATA_SCIENTIST,ADMIN,SUPPORT_OPERATOR", env="ALLOWED_ROLES")
    default_tenant_id: Optional[str] = Field(default=None, env="DEFAULT_TENANT_ID")

    @property
    def allowed_roles(self) -> List[str]:
        raw = os.getenv("ALLOWED_ROLES", self.allowed_roles_raw)
        return [item.strip() for item in raw.split(",") if item.strip()]


settings = Settings()
