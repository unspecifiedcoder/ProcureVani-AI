from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os


def _load_env_file() -> None:
    env_file = Path(__file__).resolve().parent.parent.parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass
class Settings:
    wa_verify_token: str = ""
    wa_access_token: str = ""
    wa_phone_number_id: str = ""
    gemini_api_key: str = ""
    supabase_url: str = ""
    supabase_service_key: str = ""
    redis_url: str = "redis://localhost:6379"
    pinata_jwt: str = ""
    pinata_gateway: str = "https://gateway.pinata.cloud"
    polygon_rpc_url: str = ""
    private_key: str = ""
    contract_address: str = ""
    environment: str = "development"
    base_url: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    _load_env_file()
    return Settings(
        wa_verify_token=os.getenv("WA_VERIFY_TOKEN", ""),
        wa_access_token=os.getenv("WA_ACCESS_TOKEN", ""),
        wa_phone_number_id=os.getenv("WA_PHONE_NUMBER_ID", ""),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_service_key=os.getenv("SUPABASE_SERVICE_KEY", ""),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        pinata_jwt=os.getenv("PINATA_JWT", ""),
        pinata_gateway=os.getenv("PINATA_GATEWAY", "https://gateway.pinata.cloud"),
        polygon_rpc_url=os.getenv("POLYGON_RPC_URL", ""),
        private_key=os.getenv("PRIVATE_KEY", ""),
        contract_address=os.getenv("CONTRACT_ADDRESS", ""),
        environment=os.getenv("ENVIRONMENT", "development"),
        base_url=os.getenv("BASE_URL", "http://localhost:8000"),
    )
