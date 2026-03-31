import hashlib
from typing import Any


class PinataClient:
    async def pin_json(self, payload: dict[str, Any], name: str = "metadata.json") -> dict[str, str]:
        digest = hashlib.sha256(f"{name}:{payload}".encode("utf-8")).hexdigest()[:46]
        return {
            "ipfs_hash": f"Qm{digest}",
            "name": name,
        }


pinata_client = PinataClient()
