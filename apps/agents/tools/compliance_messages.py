from typing import Any, Dict


def rating_tone(rating: str) -> str:
    tones = {
        "GREEN": "compliance_green",
        "AMBER": "compliance_amber",
        "RED": "compliance_red",
    }
    return tones.get(rating, "compliance_amber")


def format_compliance_summary(result: Dict[str, Any], product_name: str, strings: Dict[str, str]) -> str:
    template = strings.get(
        "compliance_summary",
        "Compliance result for {product}: score {score:.1f}%, threshold {threshold:.1f}%, rating {rating}.",
    )
    return template.format(
        product=product_name or "the submitted product",
        score=result.get("score", 0.0),
        threshold=result.get("threshold", 0.0),
        rating=result.get("rating", "AMBER"),
    )


def format_document_guidance(result: Dict[str, Any], strings: Dict[str, str]) -> str:
    documents = result.get("min_documents", [])
    if not documents:
        return ""
    template = strings.get("compliance_documents", "Recommended supporting documents: {documents}.")
    return template.format(documents=", ".join(documents))


def format_gap_guidance(result: Dict[str, Any], strings: Dict[str, str]) -> str:
    if result.get("compliant"):
        return ""
    return strings.get(
        "compliance_gap_help",
        "Reduce imported input value or upload stronger proof documents to improve the score.",
    )
