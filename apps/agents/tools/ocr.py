import re
from typing import Any


async def extract_from_image(image_bytes: bytes) -> dict[str, Any]:
    text = image_bytes.decode("utf-8", errors="ignore").strip()
    if not text:
        return {"raw_text": "", "fields": {}}

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    joined = " ".join(lines)
    fields = {
        "invoice_no": _extract(r"invoice\s*(?:no|number)?[:#\- ]+([A-Z0-9\-/]+)", joined),
        "supplier": _extract(r"supplier[:\- ]+(.+?)(?:\s+gstin[:\- ]+|\s+invoice\s|\s+amount[:\- ]+|$)", joined),
        "gstin": _extract(r"gstin[:\- ]+([0-9A-Z]{15})", joined),
        "amount": _extract(r"(?:amount|total)[:\- ]+([0-9,]+(?:\.[0-9]{1,2})?)", joined),
    }
    return {"raw_text": joined, "fields": fields}


def _extract(pattern: str, text: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else ""
