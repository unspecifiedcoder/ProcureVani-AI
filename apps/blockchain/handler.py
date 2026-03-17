# apps/blockchain/handler.py
# Polygon blockchain handler.

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class BlockchainHandler:
    def __init__(self):
        self._web3 = None
        self._contract = None
        self._account = None
        self._initialized = False

    def _ensure_initialised(self):
        if self._initialized:
            return
        self._initialized = True
        
        from apps.webhook.config import get_settings
        settings = get_settings()
        
        if not settings.polygon_rpc_url or not settings.private_key:
            logger.info("Blockchain not configured, using mock mode")
            return
        
        try:
            from web3 import Web3
            from eth_account import Account
            
            self._web3 = Web3(Web3.HTTPProvider(settings.polygon_rpc_url))
            if self._web3.is_connected():
                self._account = Account.from_key(settings.private_key)
                logger.info(f"Blockchain wallet: {self._account.address}")
                
                if settings.contract_address:
                    abi_path = Path(__file__).parent / "abi.json"
                    if abi_path.exists():
                        with open(abi_path) as f:
                            abi = json.load(f)
                        self._contract = self._web3.eth.contract(
                            address=settings.contract_address,
                            abi=abi
                        )
        except Exception as e:
            logger.error(f"Blockchain init failed: {e}")

    @property
    def is_configured(self) -> bool:
        self._ensure_initialised()
        return self._web3 is not None and self._contract is not None

    async def issue_passport(self, passport_id: str, msme_id: str, dpiit_no: str, product_code: str, lcv_score: float, doc_hash: str, ipfs_hash: str) -> Dict[str, Any]:
        if not self.is_configured:
            return {"success": True, "mock": True, "passport_id": passport_id, "tx_hash": "0x" + "0"*64}
        
        try:
            nonce = self._web3.eth.get_transaction_count(self._account.address)
            lcv_basis_points = int(lcv_score * 100)
            
            tx = self._contract.functions.issuePassport(passport_id, msme_id, dpiit_no, product_code, lcv_basis_points, doc_hash, ipfs_hash).build_transaction({
                "from": self._account.address,
                "nonce": nonce,
                "gas": 300000,
                "gasPrice": self._web3.eth.gas_price,
            })
            
            signed = self._web3.eth.account.sign_transaction(tx, self._account.key)
            tx_hash = self._web3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = self._web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            return {"success": True, "passport_id": passport_id, "tx_hash": tx_hash.hex(), "block_number": receipt.blockNumber}
        except Exception as e:
            logger.error(f"Issue passport failed: {e}")
            return {"success": False, "error": str(e)}

    async def verify_passport(self, passport_id: str) -> Dict[str, Any]:
        if not self.is_configured:
            return {"passport_id": passport_id, "mock": True}
        
        try:
            result = self._contract.functions.verifyPassport(passport_id).call()
            return {
                "passport_id": passport_id,
                "msme_id": result[0],
                "product_code": result[1],
                "status": result[2],
                "lcv_score": result[3] / 100,
                "doc_hash": result[4],
                "valid_until": datetime.fromtimestamp(result[5], tz=timezone.utc).isoformat(),
                "ipfs_hash": result[6],
                "on_chain": True,
            }
        except Exception as e:
            logger.error(f"Verify passport failed: {e}")
            return {"error": str(e), "on_chain": False}

blockchain_handler = BlockchainHandler()
