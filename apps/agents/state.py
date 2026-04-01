# apps/agents/state.py
# Typed state definition for LangGraph compliance pipeline.

from typing import TypedDict, Optional, Dict, Any, List

class MSMEState(TypedDict, total=False):
    wa_id: str
    language: str
    user_input: str
    reply: str
    intent: str
    intent_confidence: float
    company_name: str
    dpiit_no: str
    gstin: str
    product_name: str
    hs_code: str
    local_content_pct: float
    raw_material_value: float
    foreign_input_value: float
    compliance_result: Dict[str, Any]
    passport_id: str
    doc_hash: str
    ipfs_hash: str
    valid_until: str
    step: str
    error: str
