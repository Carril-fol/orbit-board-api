import os
from functools import lru_cache
 
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    secret_key: str
    neon_database_url: str
    server_host: str = "0.0.0.0"
    server_port: int = 8000
 
    jwt_token_location: list[str] = ["cookies"]
    jwt_access_token_expires: int = 1800
    jwt_refresh_token_expires: int = 2592000
 
    jwt_cookie_httponly: bool = True
    jwt_cookie_secure: bool = True
    jwt_cookie_samesite: str = "None"
    jwt_cookie_csrf_protect: bool = False
    jwt_csrf_in_cookies: bool = False

    cors_origins: list[str] = []
    cors_supports_credentials: bool = True

    debug: bool = False
 
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )
 
 
class DevelopmentSettings(Settings):
    debug: bool = True
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    jwt_cookie_csrf_protect: bool = False
    jwt_cookie_httponly: bool = True
    jwt_csrf_in_cookies: bool = False
    jwt_cookie_secure: bool = True
    jwt_cookie_samesite: str = "None"
 
 
class ProductionSettings(Settings):
    debug: bool = False
    jwt_cookie_csrf_protect: bool = True
    jwt_cookie_httponly: bool = True
    jwt_csrf_in_cookies: bool = True
    jwt_cookie_secure: bool = True
    jwt_cookie_samesite: str = "None"
 
 
@lru_cache
def get_settings() -> Settings:
    env: str = os.getenv("ENV", "development")
    settings_map = {
        "development": DevelopmentSettings,
        "production": ProductionSettings,
    }
    settings_class = settings_map.get(env, DevelopmentSettings)
    return settings_class()
 
 
settings = get_settings()