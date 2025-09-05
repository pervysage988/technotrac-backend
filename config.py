from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "TechnoTrac"
    database_url: str
    secret_key: str
    access_token_exp_minutes: int = Field(60 * 24, alias="ACCESS_TOKEN_EXPIRE_MINUTES") # ✅ default 24h, can override in .env

    class Config:
        env_file = ".env"
        populate_by_name = True

settings = Settings()
