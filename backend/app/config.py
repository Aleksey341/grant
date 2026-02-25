from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # App
    app_name: str = "GrantsAssistant"
    secret_key: str = "dev-secret-key-change-in-production-32chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    environment: str = "development"

    # Database
    database_url: str = "sqlite+aiosqlite:///./grants.db"

    # Anthropic
    anthropic_api_key: Optional[str] = None

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None

    # Telegram
    telegram_bot_token: Optional[str] = None

    # Web Push
    vapid_private_key: Optional[str] = None
    vapid_public_key: Optional[str] = None
    vapid_email: str = "mailto:admin@grantsassistant.com"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


def get_settings() -> Settings:
    # Build DATABASE_URL from Railway env vars if available
    pg_host = os.getenv("PGHOST")
    if pg_host and not os.getenv("DATABASE_URL"):
        pg_user = os.getenv("PGUSER", "postgres")
        pg_password = os.getenv("PGPASSWORD", "")
        pg_port = os.getenv("PGPORT", "5432")
        pg_db = os.getenv("PGDATABASE", "railway")
        os.environ["DATABASE_URL"] = (
            f"postgresql+asyncpg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
        )
    return Settings()


settings = get_settings()
