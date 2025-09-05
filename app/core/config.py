from pydantic_settings import BaseSettings
from typing import List, Union
import json


class Settings(BaseSettings):
    # ---- Application ----
    app_name: str = "TechnoTrac API"
    debug: bool = False
    access_token_exp_minutes: int = 60 * 24  # default: 1 day

    # ---- Database ----
    database_url: str

    # ---- Redis ----
    redis_url: str = "redis://localhost:6379/0"

    # ---- Security / JWT ----
    jwt_algorithm: str = "HS256"
    jwt_secret_keys: List[str]  # <- loaded from .env as JSON list

    # ---- CORS ----
    allowed_origins: Union[str, List[str]] = "[]"

    # ---- AWS / S3 ----
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str = "ap-south-1"  # default = Mumbai
    aws_s3_bucket: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    # -------------------------
    # Helpers
    # -------------------------
    @property
    def primary_secret_key(self) -> str:
        """Use the first key in the list for signing new tokens"""
        return self.jwt_secret_keys[0]

    @property
    def all_secret_keys(self) -> List[str]:
        """Return all keys (new + old) for verification"""
        return self.jwt_secret_keys

    @property
    def cors_origins(self) -> List[str]:
        """Normalize allowed origins into a list of strings"""
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
