from pathlib import Path
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    database_url: str = "sqlite:///./studymate.db"
    jwt_secret: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 1440
    gemini_api_key: str | None = None
    gemini_model: str = Field(
        default="gemini-3.6-flash",
        validation_alias=AliasChoices("GEMINI_MODEL", "LLM_MODEL"),
    )
    cors_origins: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")
settings = Settings()
