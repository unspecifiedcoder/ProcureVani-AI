# apps/agents/tools/ppp_mii.py
# PPP-MII compliance rule engine.

import json
from pathlib import Path
from typing import Dict, Any

DEFAULT_THRESHOLD = 50

def load_rules() -> Dict[str, Dict[str, Any]]:
    rules_file = Path(__file__).parent.parent.parent / "data" / "ppp_mii_rules.json"
    if rules_file.exists():
        with open(rules_file) as f:
            return json.load(f)
    return {}

PPP_MII_RULES = load_rules()

def get_hs_code_prefix(hs_code: str) -> str:
    cleaned = hs_code.replace(".", "").strip()
    return cleaned[:4] if len(cleaned) >= 4 else cleaned

def calculate_lcv(total_value: float, foreign_input_value: float) -> float:
    if total_value <= 0:
        return 0.0
    return ((total_value - foreign_input_value) / total_value) * 100

def check_compliance(hs_code: str, lcv_pct: float) -> Dict[str, Any]:
    prefix = get_hs_code_prefix(hs_code)
    rule = PPP_MII_RULES.get(prefix, {})
    threshold = rule.get("min_lcv_percent", DEFAULT_THRESHOLD)
    gap = max(0.0, threshold - lcv_pct)
    compliant = lcv_pct >= threshold
    
    if lcv_pct >= threshold + 10:
        rating = "GREEN"
    elif lcv_pct >= threshold:
        rating = "AMBER"
    else:
        rating = "RED"
    
    return {
        "compliant": compliant,
        "score": round(lcv_pct, 2),
        "threshold": threshold,
        "gap": round(gap, 2),
        "rating": rating,
        "category": rule.get("product_category", "Unknown"),
    }
