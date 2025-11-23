from pydantic import Field
from pydantic_settings import BaseSettings

DEFAULT_DB_HOST = "postgres"
DEFAULT_DB_PORT = 5432
DEFAULT_DB_NAME = "pulsecast"
DEFAULT_DB_USER = "pulsecast"
DEFAULT_DB_PASSWORD = "pulsecast"


class Settings(BaseSettings):
    """Service configuration loaded from environment variables."""

    db_host: str = Field(default=DEFAULT_DB_HOST, env="DB_HOST")
    db_port: int = Field(default=DEFAULT_DB_PORT, env="DB_PORT")
    db_name: str = Field(default=DEFAULT_DB_NAME, env="DB_NAME")
    db_user: str = Field(default=DEFAULT_DB_USER, env="DB_USER")
    db_password: str = Field(default=DEFAULT_DB_PASSWORD, env="DB_PASSWORD")

    class Config:
        case_sensitive = False


settings = Settings()
