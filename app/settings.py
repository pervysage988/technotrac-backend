# app/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV: str = "dev"
    SECRET_KEY: str

    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_EXPIRES_MIN: int = 1440

    SMS_PROVIDER: Literal["twilio", "msg91"] = "twilio"

    # Twilio
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_PHONE_NUMBER: str | None = None

    # MSG91
    MSG91_AUTH_KEY: str | None = None
    MSG91_SENDER_ID: str | None = None
    MSG91_TEMPLATE_ID: str | None = None

settings = Settings()
 
