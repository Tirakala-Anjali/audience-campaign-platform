from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "AudienceFlow API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AudienceFlow — Audience Management & Campaign Planning Platform API"

    # Use postgresql+psycopg2 to force psycopg2 dialect (psycopg2-binary installed)
    DATABASE_URL: str = "postgresql+psycopg2://postgres:password@localhost:5432/audienceflow"
    SECRET_KEY: str = "change-this-secret-key-in-production"

    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Future integrations
    OPENAI_API_KEY: str = ""
    SENDGRID_API_KEY: str = ""
    TWILIO_API_KEY: str = ""

    # pydantic-settings v2 model_config (replaces inner class Config)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # ignore extra vars in .env
    )


settings = Settings()
