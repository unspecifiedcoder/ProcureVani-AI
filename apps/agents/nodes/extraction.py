import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

from apps.agents.llm import gemini_llm
from apps.agents.state import MSMEState

CATEGORIES_PATH = Path(__file__).resolve().parents[3] / "data" / "gem_categories.json"
EXTRACTABLE_FIELDS = ["company_name", "product_name", "hs_code", "local_content_pct", "dpiit_no", "gstin"]


def _load_categories() -> list[dict[str, Any]]:
    if not CATEGORIES_PATH.exists():
        return []
    with CATEGORIES_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


GEM_CATEGORIES = _load_categories()


async def extraction_node(state: MSMEState) -> Dict[str, Any]:
    user_input = state.get("user_input", "")
    if not user_input:
        return {}

    extracted = extract_registration_fields(user_input)
    fields_needed = [field for field in EXTRACTABLE_FIELDS if not state.get(field)]
    existing_context = {field: state.get(field) for field in EXTRACTABLE_FIELDS if state.get(field)}
    llm_fields = await gemini_llm.extract_fields(user_input, fields_needed, existing_context)

    updates: Dict[str, Any] = {}
    for field in fields_needed:
        value = extracted.get(field, llm_fields.get(field))
        if value in (None, ""):
            value = llm_fields.get(field)
        if value in (None, ""):
            continue
        if field == "local_content_pct":
            try:
                updates[field] = float(str(value).replace("%", "").strip())
            except ValueError:
                continue
        else:
            updates[field] = str(value).strip()

    if extracted.get("gem_category") and not state.get("gem_category"):
        updates["gem_category"] = extracted["gem_category"]
    return updates


def extract_registration_fields(text: str) -> dict[str, Any]:
    normalized = text.strip()
    lower = normalized.lower()
    hs_code = _extract(r"\b(\d{4,8})\b", normalized)
    local_content = _extract_number(r"(?:lcv|local content)[^0-9]{0,12}(\d{1,3}(?:\.\d+)?)", lower)
    inferred = infer_category(normalized)

    return {
        "product_name": inferred.get("product_name", ""),
        "hs_code": hs_code or inferred.get("hs_code", ""),
        "local_content_pct": local_content,
        "gem_category": inferred.get("gem_category", ""),
        "missing_fields": [
            field
            for field, value in {
                "product_name": inferred.get("product_name", ""),
                "hs_code": hs_code or inferred.get("hs_code", ""),
                "local_content_pct": local_content,
            }.items()
            if value in ("", None)
        ],
    }


def infer_category(text: str) -> dict[str, str]:
    lower = text.lower()
    for item in GEM_CATEGORIES:
        if any(keyword in lower for keyword in item.get("keywords", [])):
            return {
                "product_name": _titleize_keyword(item["keywords"][0]),
                "hs_code": item["hs_code"],
                "gem_category": item["gem_category"],
            }
    return {"product_name": "", "hs_code": "", "gem_category": ""}


def _extract(pattern: str, text: str) -> str:
    match = re.search(pattern, text)
    return match.group(1) if match else ""


def _extract_number(pattern: str, text: str) -> Optional[float]:
    match = re.search(pattern, text)
    return float(match.group(1)) if match else None


def _titleize_keyword(keyword: str) -> str:
    return " ".join(token.capitalize() for token in keyword.split())
