# apps/webhook/main.py
# FastAPI application entry point.
# Mounts the WhatsApp webhook router, passport verification endpoint,
# test simulation endpoint, and health checks.

import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from apps.webhook.config import get_settings
from apps.webhook.routers import inbound
from apps.webhook.session import session_manager

# Configure logging for the entire application.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ProcureVani API",
    description=(
        "Voice-First Agentic WhatsApp + Blockchain Co-Pilot "
        "for MSME GeM Compliance (PPP-MII)"
    ),
    version="0.1.0",
)

# CORS: allow the Next.js dashboard and any development origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the WhatsApp webhook router.
app.include_router(inbound.router, prefix="/webhook", tags=["WhatsApp Webhook"])


# -- Root and health endpoints --------------------------------------------------

@app.get("/", tags=["System"])
async def root():
    settings = get_settings()
    return {
        "service": "ProcureVani API",
        "version": "0.1.0",
        "environment": settings.environment,
        "status": "running",
    }


@app.get("/health", tags=["System"])
async def health_check():
    """Lightweight health check for load balancers and monitoring."""
    return {"status": "healthy"}


# -- Passport verification endpoint --------------------------------------------

@app.get("/verify/{passport_id}", tags=["Verification"])
async def verify_passport(passport_id: str):
    """
    Public endpoint to verify a compliance passport.
    Can be called by auditors, GeM portal, or embedded in QR codes.
    """
    from apps.blockchain.handler import blockchain_handler

    result = await blockchain_handler.verify_passport(passport_id)

    if result.get("error"):
        raise HTTPException(status_code=404, detail=f"Passport {passport_id} not found")

    return {
        "passport_id": passport_id,
        "verified": True,
        "data": result,
    }


# -- Test simulation endpoint --------------------------------------------------
# Allows testing the full conversation flow without WhatsApp.

class TestMessage(BaseModel):
    """Request body for the test endpoint."""
    wa_id: str = "test_user_91XXXXXXXXXX"
    message: str
    language: Optional[str] = None


@app.post("/test/message", tags=["Testing"])
async def test_message(body: TestMessage):
    """
    Simulate a WhatsApp message for testing.
    Processes the message through the same pipeline as a real WhatsApp message
    and returns the reply directly in the response body.
    """
    from apps.webhook.routers.inbound import (
        _new_session, _process_conversation, detect_language, get_strings
    )

    wa_id = body.wa_id
    user_input = body.message
    language = body.language or detect_language(user_input)

    # Load or create session.
    session = await session_manager.get_session(wa_id)
    if session is None:
        session = _new_session(wa_id, language)

    session.setdefault("conversation_history", []).append({
        "role": "user",
        "content": user_input,
    })

    reply = await _process_conversation(user_input, session)

    session["conversation_history"].append({
        "role": "assistant",
        "content": reply,
    })

    await session_manager.save_session(wa_id, session)

    return {
        "reply": reply,
        "session": {
            "step": session.get("step"),
            "language": session.get("language"),
            "company_name": session.get("company_name"),
            "product_name": session.get("product_name"),
            "hs_code": session.get("hs_code"),
            "local_content_pct": session.get("local_content_pct"),
            "passport_id": session.get("passport_id"),
            "compliance_result": session.get("compliance_result"),
        },
    }


@app.post("/test/reset", tags=["Testing"])
async def test_reset(wa_id: str = "test_user_91XXXXXXXXXX"):
    """Clear the session for a test user."""
    await session_manager.clear_session(wa_id)
    return {"status": "session cleared", "wa_id": wa_id}


# -- Dashboard API endpoints ---------------------------------------------------
# These serve data to the Next.js auditor dashboard.

@app.get("/api/stats", tags=["Dashboard API"])
async def dashboard_stats():
    """Return aggregate statistics for the dashboard overview cards."""
    # In production, these would query Supabase.
    return {
        "total_passports": 0,
        "active": 0,
        "flagged": 0,
        "avg_lcv": 0.0,
        "message": "Connect Supabase for live data",
    }


@app.get("/api/passports", tags=["Dashboard API"])
async def list_passports(
    status: Optional[str] = Query(None, description="Filter by status: ACTIVE, REVOKED, EXPIRED"),
    limit: int = Query(50, ge=1, le=200),
):
    """List passports. In production, fetches from Supabase."""
    return {"passports": [], "total": 0, "message": "Connect Supabase for live data"}


@app.get("/api/passports/{passport_id}", tags=["Dashboard API"])
async def get_passport(passport_id: str):
    """Get detailed passport data including blockchain verification."""
    from apps.blockchain.handler import blockchain_handler
    result = await blockchain_handler.verify_passport(passport_id)
    return result
