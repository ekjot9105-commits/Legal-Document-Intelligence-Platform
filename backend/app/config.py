from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables, never source-controlled secrets."""

    storage_root: Path = Path("./data/storage")
    database_path: Path = Path("./data/lexora.sqlite3")
    max_upload_bytes: int = 15 * 1024 * 1024
    allowed_origins: str = "http://localhost:5173,http://localhost:5174"
    llm_base_url: str | None = None
    llm_api_key: SecretStr | None = None
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: float = 20.0
    llm_max_input_chars: int = 12_000
    llm_max_output_tokens: int = 1_200
    llm_requests_per_minute: int = 30

    model_config = SettingsConfigDict(env_prefix="LEXORA_", env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def llm_enabled(self) -> bool:
        """Enable external inference only when both endpoint and secret are configured."""
        return bool(self.llm_base_url and self.llm_api_key)


@lru_cache
def get_settings() -> Settings:
    """Return one immutable settings object for the application process."""
    return Settings()
