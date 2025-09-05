from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
import json


class Settings(BaseSettings):
    # ---- App ----
    app_name: str = "TechnoTrac API"
    debug: bool = False
    access_token_exp_minutes: int = 60 * 24

    # ---- Database ----
    database_url: str  # must be set in Render as DATABASE_URL

    # ---- Redis ----
    redis_url: str  # must be set in Render as REDIS_URL

    # ---- Security / JWT ----
    jwt_algorithm: str = "HS256"
    jwt_secret_keys: List[str]  # must be set in Render as JWT_SECRET_KEYS (JSON array)

    # ---- Twilio ----
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_phone_number: str | None = None

    # ---- CORS ----
    allowed_origins: Union[str, List[str]] = "[]"

    # ---- AWS / S3 (optional if not used yet) ----
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str = "ap-south-1"
    aws_s3_bucket: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def primary_secret_key(self) -> str:
        return self.jwt_secret_keys[0]

    @property
    def all_secret_keys(self) -> List[str]:
        return self.jwt_secret_keys

    @property
    def cors_origins(self) -> List[str]:
        if isinstance(self.allowed_origins, list):
            return [str(o).strip() for o in self.allowed_origins]
        raw = str(self.allowed_origins).strip()
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(o).strip() for o in parsed]
        except Exception:
            pass
        return [o.strip() for o in raw.split(",") if o.strip()]


settings = Settings()
