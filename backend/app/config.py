from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # OpenRouter (for LLM chat)
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "anthropic/claude-3.5-sonnet"

    # Model Selection (claude or cohere)
    active_model: str = "claude"  # Options: "claude" or "cohere"

    # Available Models Configuration
    claude_model: str = "anthropic/claude-3.5-sonnet"
    cohere_model: str = "cohere/command-r-plus"  # Excellent for RAG tasks

    # Database
    database_url: str

    # Qdrant Cloud
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "rag-chatbot"

    # HuggingFace Embeddings (free, runs locally)
    embedding_model: str = "all-MiniLM-L6-v2"

    # Application
    environment: str = "development"
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @property
    def current_model(self) -> str:
        """Get the currently active model based on active_model setting"""
        if self.active_model.lower() == "cohere":
            return self.cohere_model
        else:
            return self.claude_model

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

settings = Settings()
