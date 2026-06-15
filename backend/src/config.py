"""Configuration for the LexRedline Contract Engine."""

import os
from typing import Dict, Any


class Settings:
    """Application settings with sensible defaults."""

    # API settings
    API_HOST: str = os.getenv("HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("PORT", "8000"))
    API_TITLE: str = "LexRedline Contract Analysis API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "AI-powered contract review engine"

    # File upload limits
    MAX_UPLOAD_SIZE_MB: int = 50

    # Database (future: connect to team SQLite via Turso)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # LLM settings (future: for LLM-powered analysis)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")

    # Analysis settings
    MAX_CLAUSE_TEXT_LENGTH: int = 5000
    ENABLE_LLM_ANALYSIS: bool = False
    PATTERN_MATCHING_ONLY: bool = True

    # CORS
    ALLOWED_ORIGINS: list = ["*"]

    @property
    def dict(self) -> Dict[str, Any]:
        return {
            "api_host": self.API_HOST,
            "api_port": self.API_PORT,
            "api_title": self.API_TITLE,
            "api_version": self.API_VERSION,
            "pattern_matching": self.PATTERN_MATCHING_ONLY,
            "llm_enabled": self.ENABLE_LLM_ANALYSIS,
        }


settings = Settings()