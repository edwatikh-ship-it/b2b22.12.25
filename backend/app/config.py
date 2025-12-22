from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # читаем backend/.env (cwd = backend), extra игнорируем
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    API_PREFIX: str = "/api/v1"

    DATABASEURL: str = Field(
        default="", validation_alias=AliasChoices("DATABASEURL", "DATABASE_URL")
    )

    # External integrations
    CHECKO_API_KEY: str = Field(
        default="", validation_alias=AliasChoices("CHECKO_API_KEY", "CHECKOAPIKEY")
    )

    @property
    def DATABASE_URL(self) -> str:
        # Back-compat for older code paths
        return self.DATABASEURL

    ALLOWED_ORIGINS: str = ""
    JWT_SECRET: str = "change_me_dev_only"


settings = Settings()
