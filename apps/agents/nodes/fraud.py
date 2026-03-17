# apps/agents/nodes/fraud.py
# Fraud detection node.

from typing import Dict, Any, List
from apps.agents.state import MSMEState

async def fraud_node(state: MSMEState) -> Dict[str, Any]:
    flags: List[Dict[str, Any]] = []
    
    compliance = state.get("compliance_result", {})
    lcv_score = compliance.get("score", 0)
    threshold = compliance.get("threshold", 50)
    gstin = state.get("gstin", "")
    foreign_value = state.get("foreign_input_value")
    
    # Check marginal compliance
    if compliance.get("compliant") and 0 < (lcv_score - threshold) < 1.0:
        flags.append({"type": "MARGINAL_COMPLIANCE", "confidence": 0.6, "detail": "LCV very close to threshold"})
    
    # Check perfect LCV
    if lcv_score >= 100:
        flags.append({"type": "PERFECT_LCV", "confidence": 0.5, "detail": "100% local content is unusual"})
    
    # Check missing GSTIN
    if not gstin or len(gstin) < 15:
        flags.append({"type": "MISSING_GSTIN", "confidence": 0.4, "detail": "GSTIN missing or invalid"})
    
    # Check zero foreign input
    if foreign_value is not None and foreign_value == 0:
        flags.append({"type": "ZERO_FOREIGN_INPUT", "confidence": 0.5, "detail": "Zero foreign inputs unusual"})
    
    return {"fraud_flags": flags, "fraud_clean": len(flags) == 0}
