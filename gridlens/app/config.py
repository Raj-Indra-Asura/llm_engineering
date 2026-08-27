from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GridLens"
    version: str = "1.0.0"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:7860"]
    max_horizon_hours: int = 168
    max_battery_capacity_kwh: float = 10000.0
    openai_api_key: str = ""
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env")
