"""
Configuration module for PhishScope.

Handles environment variables and application settings.
"""

import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Settings:
    """Application settings loaded from environment variables."""

    # LLM Provider Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "watsonx").lower()
    LLM_MODEL: Optional[str] = os.getenv("LLM_MODEL")

    # WatsonX Configuration
    WATSONX_API_KEY: Optional[str] = os.getenv("WATSONX_API_KEY")
    WATSONX_PROJECT_ID: Optional[str] = os.getenv("WATSONX_PROJECT_ID")
    WATSONX_API_ENDPOINT: str = os.getenv(
        "WATSONX_API_ENDPOINT",
        "https://us-south.ml.cloud.ibm.com"
    )
    WATSONX_MODEL_ID: str = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")

    # RITS Configuration
    RITS_API_KEY: Optional[str] = os.getenv("RITS_API_KEY")
    RITS_API_BASE_URL: str = os.getenv("RITS_API_BASE_URL", "http://9.46.81.185:4000")

    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Application Configuration
    REPORTS_DIR: Path = Path(os.getenv("REPORTS_DIR", "./reports"))
    API_PORT: int = int(os.getenv("API_PORT", "8070"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Browser Configuration
    BROWSER_HEADLESS: bool = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
    PAGE_LOAD_TIMEOUT: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "30000"))

    @classmethod
    def is_llm_configured(cls) -> bool:
        """Check if LLM is properly configured based on the selected provider."""
        if cls.LLM_PROVIDER == "watsonx":
            return bool(cls.WATSONX_API_KEY and cls.WATSONX_PROJECT_ID)
        elif cls.LLM_PROVIDER == "rits":
            return bool(cls.RITS_API_KEY)
        elif cls.LLM_PROVIDER == "openai":
            return bool(cls.OPENAI_API_KEY)
        elif cls.LLM_PROVIDER == "ollama":
            return True  # Ollama runs locally, no API key needed
        return False


settings = Settings()
