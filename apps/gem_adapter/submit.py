# apps/gem_adapter/submit.py
# GeM submission package builder.

import json
from datetime import datetime, timezone
from typing import Dict, Any

def build_gem_declaration_metadata(passport_id: str, company_name: str, dpiit_no: str, gstin: str, product_name: str, hs_code: str, category: str, lcv_score: float, threshold: float, raw_material_value: float, foreign_input_value: float, doc_hash: str, ipfs_hash: str, valid_until: str) -> Dict[str, Any]:
    domestic_value = raw_material_value - foreign_input_value
    
    return {
        "schema_version": "2.0",
        "declaration_type": "PPP_MII_LOCAL_CONTENT",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "passport_reference": passport_id,
        "seller_details": {
            "entity_name": company_name,
            "dpiit_registration_number": dpiit_no,
            "gstin": gstin,
            "classification": "MSME",
        },
        "product_details": {
            "product_name": product_name,
            "hs_code": hs_code,
            "gem_category": category,
        },
        "local_content_declaration": {
            "total_raw_material_value_inr": round(raw_material_value, 2),
            "foreign_input_value_inr": round(foreign_input_value, 2),
            "domestic_value_inr": round(domestic_value, 2),
            "local_content_value_percent": round(lcv_score, 2),
            "minimum_threshold_percent": threshold,
            "is_compliant": lcv_score >= threshold,
        },
        "verification": {
            "document_hash_sha256": doc_hash,
            "ipfs_cid": ipfs_hash,
            "blockchain_network": "Polygon",
            "valid_until": valid_until,
        },
    }
