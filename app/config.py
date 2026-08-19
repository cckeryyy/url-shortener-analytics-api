import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    database_url_local: str

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    base_url: str = "http://localhost:8001"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def resolved_database_url(self) -> str:
        if os.getenv("RUNNING_IN_DOCKER") == "1":
            return self.database_url
        return self.database_url_local


settings = Settings()
