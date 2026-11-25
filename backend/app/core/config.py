from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "BarberGo"

    # Base de datos
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3308
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "barbergo"
    # Bases en la nube (TiDB, Aiven, PlanetScale...) exigen TLS
    DB_SSL: bool = False

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Angular
    CORS_ORIGINS: list[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()