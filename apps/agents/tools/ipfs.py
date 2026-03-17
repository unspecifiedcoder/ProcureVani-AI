# apps/agents/tools/ipfs.py
# Pinata IPFS upload client.

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PinataClient:
    def __init__(self):
        from apps.webhook.config import get_settings
        settings = get_settings()
        self.jwt = settings.pinata_jwt
        self.gateway = settings.pinata_gateway

    @property
    def is_configured(self) -> bool:
        return bool(self.jwt)

    async def pin_file(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        if not self.is_configured:
            return {"ipfs_hash": "QmMock_" + filename[:20], "mock": True}
        
        import httpx
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {"Authorization": f"Bearer {self.jwt}"}
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, headers=headers, files={"file": (filename, file_bytes)})
                data = response.json()
                return {"ipfs_hash": data.get("IpfsHash", ""), "ipfs_url": f"{self.gateway}/ipfs/{data.get('IpfsHash', '')}"}
        except Exception as e:
            logger.error(f"IPFS pin failed: {e}")
            return {"error": str(e)}

pinata_client = PinataClient()
