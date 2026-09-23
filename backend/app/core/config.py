from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Legal Document Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    
    # Environment variables from .env
    OPENAI_API_KEY: str = ""
    DATABASE_URL: str = "sqlite:///./dev.db"
    SECRET_KEY: str = "super-secret-placeholder-key"
    MAX_UPLOAD_SIZE_MB: int = 10
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
