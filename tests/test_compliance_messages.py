from apps.agents.tools.compliance_messages import (
    format_compliance_summary,
    format_document_guidance,
    format_gap_guidance,
    rating_tone,
)


STRINGS = {
    "compliance_summary": "Compliance result for {product}: score {score:.1f}%, threshold {threshold:.1f}%, rating {rating}.",
    "compliance_documents": "Recommended supporting documents: {documents}.",
    "compliance_gap_help": "Reduce imported input value or upload stronger proof documents to improve the score.",
}


def test_rating_tone_maps_status_levels() -> None:
    assert rating_tone("GREEN") == "compliance_green"
    assert rating_tone("AMBER") == "compliance_amber"
    assert rating_tone("RED") == "compliance_red"


def test_format_compliance_summary_includes_score_and_threshold() -> None:
    result = {"score": 84.2, "threshold": 50.0, "rating": "GREEN"}
    message = format_compliance_summary(result, "LED Lamps", STRINGS)
    assert "LED Lamps" in message
    assert "84.2%" in message
    assert "50.0%" in message


def test_format_document_guidance_lists_documents() -> None:
    result = {"min_documents": ["BOM statement", "supplier invoice"]}
    message = format_document_guidance(result, STRINGS)
    assert "BOM statement" in message
    assert "supplier invoice" in message


def test_format_gap_guidance_only_for_non_compliant_results() -> None:
    assert format_gap_guidance({"compliant": True}, STRINGS) == ""
    assert "Reduce imported input value" in format_gap_guidance({"compliant": False}, STRINGS)
