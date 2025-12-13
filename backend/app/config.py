from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str

    # Database
    database_url: str

    # Application
    environment: str = "development"
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

settings = Settings()
