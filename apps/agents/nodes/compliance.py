# apps/agents/nodes/compliance.py
# Compliance checking node.

from typing import Dict, Any
from apps.agents.state import MSMEState
from apps.agents.tools.ppp_mii import check_compliance, calculate_lcv

async def compliance_node(state: MSMEState) -> Dict[str, Any]:
    hs_code = state.get("hs_code", "")
    raw_value = state.get("raw_material_value")
    foreign_value = state.get("foreign_input_value")
    declared_lcv = state.get("local_content_pct")
    
    if not hs_code:
        return {"needs_field": "hs_code", "reply": "I need the HS Code for your product."}
    
    if raw_value is not None and foreign_value is not None and raw_value > 0:
        actual_lcv = calculate_lcv(raw_value, foreign_value)
    elif declared_lcv is not None:
        actual_lcv = declared_lcv
    else:
        return {"needs_field": "local_content_pct", "reply": "What is your local content percentage?"}
    
    result = check_compliance(hs_code, actual_lcv)
    
    return {
        "compliance_result": result,
        "local_content_pct": round(actual_lcv, 2),
    }
