from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    database_url: str
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    jwt_access_token_expires: int = 1800
    jwt_refresh_token_expires: int = 2592000

    invitation_expires: int = 604800
    request_retry_cooldown: int = 604800

    jwt_cookie_httponly: bool = True
    jwt_cookie_secure: bool = True
    jwt_cookie_samesite: str = "lax"

    cors_origins: list[str] = []
    cors_supports_credentials: bool = True

    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    db_ssl: bool = True


    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


class DevelopmentSettings(Settings):
    debug: bool = True
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    jwt_cookie_secure: bool = False


class ProductionSettings(Settings):
    debug: bool = False


class TestingSettings(DevelopmentSettings):
    db_ssl: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env.test",
        case_sensitive=False,
        extra="ignore", 
    )

class EnvironmentSelector(BaseSettings):
    env: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    env: str = EnvironmentSelector().env
    settings_map = {
        "development": DevelopmentSettings,
        "production": ProductionSettings,
        "testing": TestingSettings
    }
    settings_class = settings_map.get(env, DevelopmentSettings)
    return settings_class()


settings = get_settings()
