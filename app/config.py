from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: int = 5432
    postgres_host: str = "postgres"
    
    environment: Literal["development", "staging", "production"] = "production"
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file='.env',
        extra="ignore",
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    @property
    def is_dev(self) -> bool:
        self.environment == "development"
    
    @property
    def is_staging(self) -> bool:
        self.environment == "staging"
    
    @property
    def is_prod(self) -> bool:
        self.environment == "development"
        
settings = Settings()