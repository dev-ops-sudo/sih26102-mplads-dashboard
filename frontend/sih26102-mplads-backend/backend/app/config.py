from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_prefix="MPLADS_",
        extra="ignore",
    )

    environment: str = "development"
    app_name: str = "MPLADS Intelligence API"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./backend/mplads.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    seed_demo_data: bool = True

    auth_enabled: bool = False
    oidc_issuer_url: str = "http://localhost:8080/realms/mplads"
    oidc_jwks_url: str = "http://localhost:8080/realms/mplads/protocol/openid-connect/certs"
    oidc_audience: str = "mplads-dashboard"
    dev_user_id: str = "demo-officer"
    dev_user_name: str = "MoSPI Demo Officer"

    redis_url: str = "redis://localhost:6379/0"
    celery_enabled: bool = False

    storage_backend: str = "local"
    local_upload_dir: Path = Path("work/uploads")
    s3_endpoint_url: str | None = None
    s3_public_endpoint_url: str | None = None
    s3_region: str = "ap-south-1"
    s3_bucket: str = "mplads-evidence"
    s3_access_key: str | None = None
    s3_secret_key: str | None = None

    openai_api_key: str | None = None
    openai_model: str = "gpt-5.4"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip().startswith("["):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith("postgresql")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
