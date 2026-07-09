from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: int = 5432
    postgres_host: str = 'postgres_red'

    environment: Literal["development", "staging", "production"] = "production"
    debug: bool = False

    @property
    def database_url(self) -> str:
        return (
            f"postgressql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    groq_api_key: str = ''

    qdrant_service_host: str = 'qdrant'
    qdrant_service_http_port: str
    qdrant_service_grpc_port: str
    qdrant_service_read_only_api_key: str
    qdrant_service_api_key: str
    qdrant_service_prefer_grpc: bool = False

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8", case_sensitive=False
    )

    @property
    def is_dev(self) -> bool:
        return self.environment == "development"

    @property
    def is_staging(self) -> bool:
        return self.environment == "staging"

    @property
    def is_prod(self) -> bool:
        return self.environment == "production"


settings = Settings()
