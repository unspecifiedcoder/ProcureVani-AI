import json
from pathlib import Path
from typing import Any


RULES_PATH = Path(__file__).resolve().parents[3] / "data" / "ppp_mii_rules.json"


def load_rules() -> dict[str, dict[str, Any]]:
    if not RULES_PATH.exists():
        return {}
    with RULES_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


PPP_MII_RULES = load_rules()


def calculate_lcv(total_value: float, foreign_input_value: float) -> float:
    if total_value <= 0:
        return 0.0
    return round(((total_value - foreign_input_value) / total_value) * 100, 2)


def check_compliance(hs_code: str, lcv_pct: float) -> dict[str, Any]:
    prefix = hs_code[:4]
    rule = PPP_MII_RULES.get(prefix, {})
    threshold = float(rule.get("threshold", 50))
    gap = max(0.0, round(threshold - lcv_pct, 2))

    if lcv_pct >= threshold + 10:
        rating = "GREEN"
    elif lcv_pct >= threshold:
        rating = "AMBER"
    else:
        rating = "RED"

    return {
        "compliant": lcv_pct >= threshold,
        "score": round(lcv_pct, 2),
        "threshold": threshold,
        "gap": gap,
        "rating": rating,
        "category": rule.get("category", "Unmapped category"),
        "policy_reference": rule.get("policy_reference", "Default threshold"),
    }
