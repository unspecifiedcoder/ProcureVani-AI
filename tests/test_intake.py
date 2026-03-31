from apps.agents.nodes.extraction import extract_registration_fields
from apps.agents.tools.ocr import extract_from_image


def test_extract_registration_fields_infers_category() -> None:
    payload = extract_registration_fields("Register LED lamp with local content 84 and hs code 8539")
    assert payload["product_name"] == "Led Lamp"
    assert payload["hs_code"] == "8539"
    assert payload["local_content_pct"] == 84.0
    assert payload["missing_fields"] == []


async def test_extract_from_image_parses_invoice_text() -> None:
    image_bytes = b"Supplier: Bharat Components GSTIN: 36ABCDE1234F1Z5 Invoice No: INV-104 Amount: 45000"
    payload = await extract_from_image(image_bytes)
    assert payload["fields"]["supplier"] == "Bharat Components GSTIN"
    assert payload["fields"]["gstin"] == "36ABCDE1234F1Z5"
    assert payload["fields"]["invoice_no"] == "INV-104"
