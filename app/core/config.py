from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List, Union
import json


class Settings(BaseSettings):
    # ---- App ----
    app_name: str = "TechnoTrac API"
    debug: bool = False
    access_token_exp_minutes: int = Field(60 * 24, alias="ACCESS_TOKEN_EXP_MINUTES")

    # ---- Database ----
    database_url: str = Field(..., alias="DATABASE_URL")

    # ---- Redis ----
    redis_url: str = Field(..., alias="REDIS_URL")

    # ---- Security / JWT ----
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    jwt_secret_keys: List[str] = Field(..., alias="JWT_SECRET_KEYS")

    # ---- Twilio ----
    twilio_account_sid: str | None = Field(None, alias="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str | None = Field(None, alias="TWILIO_AUTH_TOKEN")
    twilio_phone_number: str | None = Field(None, alias="TWILIO_PHONE_NUMBER")

    # ---- CORS ----
    allowed_origins: Union[str, List[str]] = Field("[]", alias="ALLOWED_ORIGINS")

    # ---- AWS / S3 ----
    aws_access_key_id: str | None = Field(None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str | None = Field(None, alias="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field("ap-south-1", alias="AWS_REGION")
    aws_s3_bucket: str | None = Field(None, alias="AWS_S3_BUCKET")

    # ---- Model config ----
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------
    # ✅ Validators
    # -------------------------
    @field_validator("jwt_secret_keys", mode="before")
    def parse_jwt_keys(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [v]
        return v

    @field_validator("allowed_origins", mode="before")
    def parse_cors(cls, v):
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [o.strip() for o in v.split(",") if o.strip()]
        return v

    # -------------------------
    # ✅ Helper properties
    # -------------------------
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
        return []


settings = Settings()
