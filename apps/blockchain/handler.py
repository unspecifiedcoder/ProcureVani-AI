from datetime import datetime, timedelta
from typing import Any


class BlockchainHandler:
    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    async def issue_passport(
        self,
        passport_id: str,
        msme_id: str,
        dpiit_no: str,
        product_code: str,
        lcv_score: float,
        doc_hash: str,
        ipfs_hash: str,
    ) -> dict[str, Any]:
        issued_at = datetime.utcnow()
        record = {
            "passport_id": passport_id,
            "msme_id": msme_id,
            "dpiit_no": dpiit_no,
            "product_code": product_code,
            "lcv_score": round(lcv_score, 2),
            "doc_hash": doc_hash,
            "ipfs_hash": ipfs_hash,
            "issued_at": issued_at.isoformat(),
            "valid_until": (issued_at + timedelta(days=365)).isoformat(),
            "status": "ACTIVE",
            "on_chain": False,
            "tx_hash": f"0x{passport_id.lower().replace('-', '')}mock",
        }
        self._store[passport_id] = record
        return record

    async def verify_passport(self, passport_id: str) -> dict[str, Any]:
        return self._store.get(passport_id, {"error": "not_found"})


blockchain_handler = BlockchainHandler()
