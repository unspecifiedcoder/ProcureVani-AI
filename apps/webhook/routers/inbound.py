# apps/webhook/routers/inbound.py
# WhatsApp webhook endpoint.
# Receives inbound messages from the Meta WhatsApp Business Cloud API,
# processes them through the LangGraph compliance pipeline, and sends
# a reply back to the user.

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse

from apps.webhook.config import get_settings
from apps.webhook.session import session_manager
from apps.webhook.whatsapp import whatsapp_client
from apps.agents.llm import gemini_llm
from apps.agents.tools.ppp_mii import check_compliance, calculate_lcv
from apps.agents.tools.stt import transcribe_audio
from apps.agents.tools.ocr import extract_from_image

logger = logging.getLogger(__name__)
router = APIRouter()

# -- Language helpers -----------------------------------------------------------

_LANG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "languages"
_LANG_CACHE: Dict[str, Dict[str, str]] = {}


def detect_language(text: str) -> str:
    """Detect language from Unicode script ranges present in the text."""
    if re.search(r"[\u0C00-\u0C7F]", text):
        return "te"
    if re.search(r"[\u0900-\u097F]", text):
        return "hi"
    return "en"


def get_strings(lang: str) -> Dict[str, str]:
    """Load language strings from the data/languages directory with caching."""
    if lang in _LANG_CACHE:
        return _LANG_CACHE[lang]
    lang_file = _LANG_DIR / f"{lang}.json"
    if lang_file.exists():
        with open(lang_file, encoding="utf-8") as fh:
            strings = json.load(fh)
            _LANG_CACHE[lang] = strings
            return strings
    return {}


# -- WhatsApp webhook verification (GET) ---------------------------------------

@router.get("")
async def verify_webhook(
    request: Request,
):
    """
    Handle the WhatsApp webhook verification challenge.
    Meta sends a GET request with hub.mode, hub.verify_token, and hub.challenge.
    """
    settings = get_settings()
    params = request.query_params

    hub_mode = params.get("hub.mode")
    hub_token = params.get("hub.verify_token")
    hub_challenge = params.get("hub.challenge")

    if hub_mode == "subscribe" and hub_token == settings.wa_verify_token:
        logger.info("Webhook verification succeeded")
        return PlainTextResponse(content=hub_challenge, status_code=200)

    logger.warning("Webhook verification failed: mode=%s", hub_mode)
    raise HTTPException(status_code=403, detail="Verification failed")


# -- WhatsApp message receiver (POST) -----------------------------------------

@router.post("")
async def receive_message(request: Request):
    """
    Receive and process inbound WhatsApp messages.
    Supports text, audio (voice notes), and image messages.
    """
    body = await request.json()

    # Guard: not all webhook payloads contain messages (e.g. delivery receipts).
    entry = body.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    value = changes.get("value", {})

    if "messages" not in value:
        return {"status": "ok"}

    messages = value.get("messages", [])
    if not messages:
        return {"status": "ok"}

    msg = messages[0]
    wa_id = msg.get("from", "")
    msg_type = msg.get("type", "")

    # Extract user input based on message type.
    user_input = await _extract_user_input(msg, msg_type, wa_id)
    if not user_input:
        return {"status": "ok"}

    # Load or create session.
    session = await session_manager.get_session(wa_id)
    if session is None:
        language = detect_language(user_input)
        session = _new_session(wa_id, language)

    # Record the user message.
    session.setdefault("conversation_history", []).append({
        "role": "user",
        "content": user_input,
    })

    # Process through the conversational state machine.
    reply = await _process_conversation(user_input, session)

    # Record the assistant reply.
    session["conversation_history"].append({
        "role": "assistant",
        "content": reply,
    })

    # Persist session.
    await session_manager.save_session(wa_id, session)

    # Send reply to WhatsApp.
    await whatsapp_client.send_text(wa_id, reply)

    return {"status": "ok"}


# -- Input extraction ----------------------------------------------------------

async def _extract_user_input(msg: Dict, msg_type: str, wa_id: str) -> Optional[str]:
    """Extract text from a WhatsApp message, transcribing audio or OCR-ing images."""

    if msg_type == "text":
        return msg.get("text", {}).get("body", "").strip()

    if msg_type == "audio":
        audio_id = msg.get("audio", {}).get("id")
        if not audio_id:
            return None
        media_url = await whatsapp_client.get_media_url(audio_id)
        if media_url:
            audio_bytes = await whatsapp_client.download_media(media_url)
            if audio_bytes:
                return await transcribe_audio(audio_bytes)
        return "[Voice message received]"

    if msg_type == "image":
        image_id = msg.get("image", {}).get("id")
        caption = msg.get("image", {}).get("caption", "")
        if not image_id:
            return caption or None
        media_url = await whatsapp_client.get_media_url(image_id)
        if media_url:
            image_bytes = await whatsapp_client.download_media(media_url)
            if image_bytes:
                ocr_result = await extract_from_image(image_bytes)
                raw_text = ocr_result.get("raw_text", "")
                if caption:
                    return f"{caption}\n[OCR from image: {raw_text}]"
                return f"[OCR from image: {raw_text}]"
        return caption or "[Image received]"

    return None


# -- Session factory -----------------------------------------------------------

def _new_session(wa_id: str, language: str) -> Dict[str, Any]:
    """Create a fresh session for a new user."""
    return {
        "wa_id": wa_id,
        "language": language,
        "step": "welcome",
        "conversation_history": [],
    }


# -- Conversational state machine ----------------------------------------------
# This is a structured conversation flow that collects required data step by step.
# Once all fields are collected, it runs compliance checking, document generation,
# and passport issuance.

REGISTRATION_STEPS = [
    ("company_name", "Please tell me your company name.", "What is your company name?"),
    ("product_name", "Which product do you want to register for compliance?", "Which product?"),
    ("hs_code", "What is the HS Code for this product? For example: 8539 for LED lamps, 8471 for computers, 5208 for cotton fabric.", "HS Code?"),
    ("local_content_pct", "What is the local content percentage of your product? Enter a number like 75.", "Local content %?"),
    ("dpiit_no", "Please provide your DPIIT registration number.", "DPIIT number?"),
    ("gstin", "Please provide your GSTIN.", "GSTIN?"),
    ("raw_material_value", "What is the total raw material value in INR? Enter a number.", "Total raw material value (INR)?"),
    ("foreign_input_value", "What is the value of foreign/imported inputs in INR? Enter a number.", "Foreign input value (INR)?"),
]


async def _process_conversation(user_input: str, session: Dict[str, Any]) -> str:
    """
    Main conversation handler. Routes based on the current step in the session.
    """
    step = session.get("step", "welcome")
    language = session.get("language", "en")
    strings = get_strings(language)
    user_lower = user_input.lower().strip()

    # -- WELCOME step: classify intent --
    if step == "welcome":
        return await _handle_welcome(user_input, user_lower, session, strings)

    # -- REGISTRATION flow: collect fields one by one --
    if step.startswith("collect_"):
        return await _handle_collection(user_input, session, strings)

    # -- CHECK STATUS --
    if step == "check_status":
        return await _handle_check_status(user_input, session, strings)

    # -- COMPLIANCE RESULT already given, user might want to restart --
    if step in ("compliance_pass", "compliance_fail", "passport_issued"):
        return await _handle_post_compliance(user_input, user_lower, session, strings)

    # Fallback: treat as new conversation.
    session["step"] = "welcome"
    return strings.get("welcome", "Welcome to ProcureVani. How can I help you?")


async def _handle_welcome(
    user_input: str, user_lower: str, session: Dict, strings: Dict
) -> str:
    """Handle the initial user message, classifying intent."""

    # Use the LLM for intent classification.
    intent_result = await gemini_llm.classify_intent(user_input, session.get("language", "en"))
    intent = intent_result.get("intent", "other")

    if intent == "register" or any(kw in user_lower for kw in ["register", "new", "start", "hi", "hello", "namaste"]):
        session["step"] = "collect_company_name"
        welcome_msg = strings.get("welcome", "Welcome to ProcureVani!")
        return (
            f"{welcome_msg}\n\n"
            "I will help you check PPP-MII compliance and generate a Compliance Passport "
            "for GeM procurement.\n\n"
            "Let us start. What is your company name?"
        )

    if intent == "check_status":
        session["step"] = "check_status"
        return "Please provide your Passport ID (e.g. PV-A3F2B1C9) or DPIIT registration number."

    if intent == "help":
        return strings.get("help_text", (
            "ProcureVani helps MSMEs with GeM compliance.\n"
            "1. Register -- check PPP-MII compliance and get a Compliance Passport\n"
            "2. Check Status -- verify an existing passport\n"
            "3. Query -- ask questions about the process\n\n"
            "Send 'register' to begin."
        ))

    if intent == "query":
        reply = await gemini_llm.generate_reply(user_input, session, session.get("language", "en"))
        return reply

    # Default: show welcome.
    return strings.get("welcome", "Welcome to ProcureVani. Send 'register' to begin, 'status' to check, or 'help' for guidance.")


async def _handle_collection(user_input: str, session: Dict, strings: Dict) -> str:
    """
    Handle the step-by-step data collection for MSME registration.
    Each step collects one field and advances to the next.
    """
    step = session.get("step", "")
    current_field = step.replace("collect_", "")

    # Find the current field index.
    field_index = -1
    for idx, (field_name, _, _) in enumerate(REGISTRATION_STEPS):
        if field_name == current_field:
            field_index = idx
            break

    if field_index == -1:
        session["step"] = "welcome"
        return "Something went wrong. Let us start over. Send 'register' to begin."

    field_name = REGISTRATION_STEPS[field_index][0]

    # Validate and store the value.
    numeric_fields = {"local_content_pct", "raw_material_value", "foreign_input_value"}
    if field_name in numeric_fields:
        try:
            cleaned = user_input.replace("%", "").replace(",", "").replace("INR", "").replace("Rs", "").strip()
            value = float(cleaned)
            session[field_name] = value
        except ValueError:
            return f"Please enter a valid number. For example: 75000"
    else:
        session[field_name] = user_input.strip()

    # Advance to the next field.
    next_index = field_index + 1

    if next_index < len(REGISTRATION_STEPS):
        next_field_name, prompt_en, prompt_short = REGISTRATION_STEPS[next_index]
        session["step"] = f"collect_{next_field_name}"
        return prompt_en

    # All fields collected. Run compliance check.
    return await _run_compliance(session, strings)


async def _run_compliance(session: Dict, strings: Dict) -> str:
    """
    All registration data is collected. Run the compliance engine,
    generate documents, and issue the passport.
    """
    import hashlib
    from datetime import datetime, timedelta

    hs_code = session.get("hs_code", "")
    raw_value = session.get("raw_material_value", 0)
    foreign_value = session.get("foreign_input_value", 0)
    declared_lcv = session.get("local_content_pct", 0)

    # Recalculate LCV from raw values if they make sense.
    if raw_value > 0:
        actual_lcv = calculate_lcv(raw_value, foreign_value)
    else:
        actual_lcv = declared_lcv

    session["local_content_pct"] = round(actual_lcv, 2)

    result = check_compliance(hs_code, actual_lcv)
    session["compliance_result"] = result

    if not result["compliant"]:
        session["step"] = "compliance_fail"
        gap = result["gap"]
        non_compliant_msg = strings.get("non_compliant", "Your product does not meet the PPP-MII threshold.").format(gap=gap)
        return (
            f"{non_compliant_msg}\n\n"
            f"Product: {session.get('product_name', 'N/A')}\n"
            f"HS Code: {hs_code} ({result.get('category', 'Unknown')})\n"
            f"Your LCV: {actual_lcv:.1f}%\n"
            f"Required threshold: {result['threshold']}%\n"
            f"Gap: {gap:.1f}%\n"
            f"Rating: {result['rating']}\n\n"
            "You need to increase local content by reducing foreign inputs. "
            "Send 'register' to try again with updated values."
        )

    # Compliant -- generate passport.
    passport_id = "PV-" + hashlib.sha256(
        f"{session.get('dpiit_no', '')}|{session.get('product_name', '')}|{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:8].upper()

    valid_until = (datetime.utcnow() + timedelta(days=365)).strftime("%d %b %Y")

    doc_content = (
        f"{passport_id}|{session.get('company_name', '')}|{session.get('dpiit_no', '')}|"
        f"{session.get('product_name', '')}|{actual_lcv}"
    )
    doc_hash = hashlib.sha256(doc_content.encode()).hexdigest()

    session["passport_id"] = passport_id
    session["valid_until"] = valid_until
    session["doc_hash"] = doc_hash
    session["step"] = "passport_issued"

    # Issue on blockchain (async, non-blocking if not configured).
    try:
        from apps.blockchain.handler import blockchain_handler
        blockchain_result = await blockchain_handler.issue_passport(
            passport_id=passport_id,
            msme_id=session.get("wa_id", ""),
            dpiit_no=session.get("dpiit_no", ""),
            product_code=hs_code,
            lcv_score=actual_lcv,
            doc_hash=doc_hash,
            ipfs_hash="",  # IPFS pinning happens separately.
        )
        tx_hash = blockchain_result.get("tx_hash", "N/A")
    except Exception as exc:
        logger.error("Blockchain issuance failed: %s", exc)
        tx_hash = "pending"

    # Pin metadata to IPFS.
    ipfs_hash = ""
    try:
        from apps.agents.tools.ipfs import pinata_client
        ipfs_result = await pinata_client.pin_json(
            {
                "passport_id": passport_id,
                "company": session.get("company_name", ""),
                "product": session.get("product_name", ""),
                "hs_code": hs_code,
                "lcv_score": actual_lcv,
                "doc_hash": doc_hash,
            },
            name=f"{passport_id}_metadata.json",
        )
        ipfs_hash = ipfs_result.get("ipfs_hash", "")
        session["ipfs_hash"] = ipfs_hash
    except Exception as exc:
        logger.error("IPFS pinning failed: %s", exc)

    settings = get_settings()
    verify_url = f"{settings.base_url}/verify/{passport_id}"

    compliant_msg = strings.get("compliant", "Congratulations! You are PPP-MII compliant.")

    return (
        f"{compliant_msg}\n\n"
        f"Compliance Passport Issued!\n"
        f"---\n"
        f"Passport ID: {passport_id}\n"
        f"Company: {session.get('company_name', 'N/A')}\n"
        f"Product: {session.get('product_name', 'N/A')}\n"
        f"HS Code: {hs_code} ({result.get('category', 'Unknown')})\n"
        f"LCV Score: {actual_lcv:.1f}% (Threshold: {result['threshold']}%)\n"
        f"Rating: {result['rating']}\n"
        f"Valid until: {valid_until}\n"
        f"Blockchain TX: {tx_hash}\n"
        f"---\n"
        f"Verify: {verify_url}\n\n"
        "Your GeM submission package is being prepared. "
        "Send 'register' to check another product, or 'status' to verify a passport."
    )


async def _handle_check_status(user_input: str, session: Dict, strings: Dict) -> str:
    """Handle passport verification requests."""
    passport_id = user_input.strip().upper()

    # Validate format.
    if not passport_id.startswith("PV-"):
        # Maybe they entered a DPIIT number. Try to look it up.
        session["step"] = "welcome"
        return (
            f"I could not find a passport with ID '{user_input}'. "
            "Passport IDs start with 'PV-'. Please try again or send 'register' to begin."
        )

    try:
        from apps.blockchain.handler import blockchain_handler
        result = await blockchain_handler.verify_passport(passport_id)

        if result.get("error"):
            session["step"] = "welcome"
            return f"Passport {passport_id} was not found on the blockchain. It may not exist or may have expired."

        session["step"] = "welcome"
        return (
            f"Passport Verification Result\n"
            f"---\n"
            f"Passport ID: {passport_id}\n"
            f"Status: {result.get('status', 'Unknown')}\n"
            f"MSME ID: {result.get('msme_id', 'N/A')}\n"
            f"Product: {result.get('product_code', 'N/A')}\n"
            f"LCV Score: {result.get('lcv_score', 0):.1f}%\n"
            f"Valid Until: {result.get('valid_until', 'N/A')}\n"
            f"On-chain: {'Yes' if result.get('on_chain') else 'Mock mode'}\n"
            f"---\n"
            "Send 'register' to check another product."
        )
    except Exception as exc:
        logger.error("Status check failed: %s", exc)
        session["step"] = "welcome"
        return f"Unable to verify passport at this time. Error: {exc}"


async def _handle_post_compliance(
    user_input: str, user_lower: str, session: Dict, strings: Dict
) -> str:
    """Handle messages after compliance result has been given."""
    if any(kw in user_lower for kw in ["register", "new", "start", "again"]):
        # Reset session for a new registration, preserving identity fields.
        wa_id = session.get("wa_id", "")
        language = session.get("language", "en")
        new_session = _new_session(wa_id, language)
        session.clear()
        session.update(new_session)
        session["step"] = "collect_company_name"
        return "Starting a new compliance check.\n\nWhat is your company name?"

    if any(kw in user_lower for kw in ["status", "check", "verify"]):
        session["step"] = "check_status"
        return "Please provide the Passport ID to verify (e.g. PV-A3F2B1C9)."

    # General question -- use LLM.
    reply = await gemini_llm.generate_reply(user_input, session, session.get("language", "en"))
    return reply
