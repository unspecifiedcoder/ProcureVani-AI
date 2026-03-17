# apps/agents/nodes/document.py
# Document generation node.

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from apps.agents.state import MSMEState

def generate_passport_id(dpiit_no: str, product_name: str) -> str:
    raw = f"{dpiit_no}|{product_name}|{datetime.now(timezone.utc).isoformat()}"
    return "PV-" + hashlib.sha256(raw.encode()).hexdigest()[:8].upper()

async def document_node(state: MSMEState) -> Dict[str, Any]:
    passport_id = generate_passport_id(
        state.get("dpiit_no", "UNKNOWN"),
        state.get("product_name", "UNKNOWN")
    )
    
    valid_until = (datetime.now(timezone.utc) + timedelta(days=365)).strftime("%d %b %Y")
    
    doc_content = f"{passport_id}|{state.get('company_name', '')}|{state.get('dpiit_no', '')}"
    doc_hash = hashlib.sha256(doc_content.encode()).hexdigest()
    
    return {
        "passport_id": passport_id,
        "doc_hash": doc_hash,
        "valid_until": valid_until,
    }
