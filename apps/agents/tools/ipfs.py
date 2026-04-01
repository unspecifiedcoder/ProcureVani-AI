import hashlib
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class PinataClient:
    def __init__(self) -> None:
        from apps.webhook.config import get_settings

        settings = get_settings()
        self.jwt = settings.pinata_jwt
        self.gateway = settings.pinata_gateway

    @property
    def is_configured(self) -> bool:
        return bool(self.jwt)

    async def pin_file(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        if not self.is_configured:
            digest = hashlib.sha256(f"{filename}:{file_bytes[:32]}".encode("utf-8", errors="ignore")).hexdigest()[:46]
            return {
                "ipfs_hash": f"Qm{digest}",
                "ipfs_url": f"{self.gateway}/ipfs/Qm{digest}",
                "mock": True,
            }

        import httpx

        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {"Authorization": f"Bearer {self.jwt}"}
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, headers=headers, files={"file": (filename, file_bytes)})
                response.raise_for_status()
                data = response.json()
                return {
                    "ipfs_hash": data.get("IpfsHash", ""),
                    "ipfs_url": f"{self.gateway}/ipfs/{data.get('IpfsHash', '')}",
                }
        except Exception as exc:
            logger.error("IPFS pin failed: %s", exc)
            return {"error": str(exc)}

    async def pin_json(self, payload: Dict[str, Any], name: str = "metadata.json") -> Dict[str, str]:
        if not self.is_configured:
            digest = hashlib.sha256(f"{name}:{payload}".encode("utf-8")).hexdigest()[:46]
            ipfs_hash = f"Qm{digest}"
            return {
                "ipfs_hash": ipfs_hash,
                "ipfs_url": f"{self.gateway}/ipfs/{ipfs_hash}",
                "name": name,
            }

        import httpx

        url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
        headers = {
            "Authorization": f"Bearer {self.jwt}",
            "Content-Type": "application/json",
        }
        body = {
            "pinataContent": payload,
            "pinataMetadata": {"name": name},
        }
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, headers=headers, json=body)
                response.raise_for_status()
                data = response.json()
                return {
                    "ipfs_hash": data.get("IpfsHash", ""),
                    "ipfs_url": f"{self.gateway}/ipfs/{data.get('IpfsHash', '')}",
                    "name": name,
                }
        except Exception as exc:
            logger.error("IPFS JSON pin failed: %s", exc)
            return {"error": str(exc), "name": name}


pinata_client = PinataClient()
