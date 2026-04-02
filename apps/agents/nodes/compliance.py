# apps/agents/nodes/compliance.py
# Compliance checking node.

from typing import Dict, Any

from apps.agents.state import MSMEState
from apps.agents.tools.ppp_mii import check_compliance, calculate_lcv
from apps.agents.tools.compliance_messages import (
    format_compliance_summary,
    format_document_guidance,
    format_gap_guidance,
    rating_tone,
)


def _default_strings() -> Dict[str, str]:
    return {
        "compliance_summary": "Compliance result for {product}: score {score:.1f}%, threshold {threshold:.1f}%, rating {rating}.",
        "compliance_documents": "Recommended supporting documents: {documents}.",
        "compliance_gap_help": "Reduce imported input value or upload stronger proof documents to improve the score.",
        "compliance_green": "Green rating: your local content comfortably clears the threshold.",
        "compliance_amber": "Amber rating: your local content clears the threshold but has a thin safety margin.",
        "compliance_red": "Red rating: your product is below the required local content threshold.",
    }

async def compliance_node(state: MSMEState) -> Dict[str, Any]:
    hs_code = state.get("hs_code", "")
    raw_value = state.get("raw_material_value")
    foreign_value = state.get("foreign_input_value")
    declared_lcv = state.get("local_content_pct")
    strings = state.get("strings", _default_strings())
    
    if not hs_code:
        return {"needs_field": "hs_code", "reply": "I need the HS Code for your product."}
    
    if raw_value is not None and foreign_value is not None and raw_value > 0:
        actual_lcv = calculate_lcv(raw_value, foreign_value)
    elif declared_lcv is not None:
        actual_lcv = declared_lcv
    else:
        return {"needs_field": "local_content_pct", "reply": "What is your local content percentage?"}
    
    result = check_compliance(hs_code, actual_lcv)
    summary = format_compliance_summary(result, state.get("product_name", ""), strings)
    doc_guidance = format_document_guidance(result, strings)
    gap_guidance = format_gap_guidance(result, strings)
    tone = strings.get(rating_tone(result["rating"]), result["rating"])
    guidance = "\n".join(part for part in [tone, doc_guidance, gap_guidance] if part)
    
    return {
        "compliance_result": result,
        "local_content_pct": round(actual_lcv, 2),
        "threshold": result["threshold"],
        "compliance_gap": result["gap"],
        "buyer_class": result.get("buyer_class", "Class I Local Supplier"),
        "compliance_summary": summary,
        "compliance_guidance": guidance,
        "reply": "\n\n".join(part for part in [summary, guidance] if part),
    }
