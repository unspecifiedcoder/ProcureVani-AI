# apps/agents/nodes/extraction.py
# Data extraction node.

from typing import Dict, Any
from apps.agents.state import MSMEState
from apps.agents.llm import gemini_llm

EXTRACTABLE_FIELDS = ["company_name", "product_name", "hs_code", "local_content_pct", "dpiit_no", "gstin"]

async def extraction_node(state: MSMEState) -> Dict[str, Any]:
    user_input = state.get("user_input", "")
    if not user_input:
        return {}
    
    fields_needed = [f for f in EXTRACTABLE_FIELDS if not state.get(f)]
    
    if not fields_needed:
        return {}
    
    existing_context = {f: state.get(f) for f in EXTRACTABLE_FIELDS if state.get(f)}
    extracted = await gemini_llm.extract_fields(user_input, fields_needed, existing_context)
    
    updates = {}
    for field in fields_needed:
        value = extracted.get(field)
        if value is None:
            continue
        if field in ("local_content_pct",):
            try:
                updates[field] = float(str(value).replace("%", "").strip())
            except:
                continue
        else:
            updates[field] = str(value).strip()
    
    return updates
