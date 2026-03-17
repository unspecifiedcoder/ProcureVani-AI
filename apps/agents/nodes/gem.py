# apps/agents/nodes/gem.py
# GeM submission package node.

from typing import Dict, Any
from apps.agents.state import MSMEState

async def gem_node(state: MSMEState) -> Dict[str, Any]:
    compliance = state.get("compliance_result", {})
    
    gem_metadata = {
        "declaration_type": "PPP-MII_Local_Content",
        "passport_id": state.get("passport_id", ""),
        "msme": {
            "company_name": state.get("company_name", ""),
            "dpiit_registration_number": state.get("dpiit_no", ""),
            "gstin": state.get("gstin", ""),
        },
        "product": {
            "name": state.get("product_name", ""),
            "hs_code": state.get("hs_code", ""),
        },
        "compliance": {
            "local_content_value_percent": state.get("local_content_pct", 0),
            "threshold_percent": compliance.get("threshold", 50),
            "rating": compliance.get("rating", ""),
            "is_compliant": compliance.get("compliant", False),
        },
    }
    
    return {"gem_ready": True, "gem_package_url": ""}
