# apps/webhook/config.py
# Centralized application configuration loaded from environment variables.
# Every other module that needs settings should import get_settings() from here.

import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All application settings, loaded from .env or environment variables."""

    # -- WhatsApp Business API --
    wa_verify_token: str = ""
    wa_access_token: str = ""
    wa_phone_number_id: str = ""

    # -- Google Gemini LLM --
    gemini_api_key: str = ""

    # -- Supabase (Postgres) --
    supabase_url: str = ""
    supabase_service_key: str = ""

    # -- Redis session cache --
    redis_url: str = "redis://localhost:6379"

    # -- IPFS / Pinata --
    pinata_jwt: str = ""
    pinata_gateway: str = "https://gateway.pinata.cloud"

    # -- Polygon blockchain --
    polygon_rpc_url: str = ""
    private_key: str = ""
    contract_address: str = ""

    # -- Application --
    environment: str = "development"
    base_url: str = "http://localhost:8000"

    # Resolve the .env file relative to the project root.
    # When running via `uvicorn apps.webhook.main:app` from the repo root,
    # Path(__file__).resolve().parent.parent.parent lands on the repo root.
    class Config:
        env_file = str(Path(__file__).resolve().parent.parent.parent / ".env")
        env_file_encoding = "utf-8"
        extra = "allow"


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()
