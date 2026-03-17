# apps/agents/llm.py
# Google Gemini LLM wrapper for intent classification and field extraction.

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class GeminiLLM:
    def __init__(self):
        self._model = None
        self._initialized = False

    def _ensure_model(self):
        if self._initialized:
            return
        self._initialized = True
        from apps.webhook.config import get_settings
        settings = get_settings()
        if not settings.gemini_api_key:
            logger.warning("GEMINI_API_KEY not set")
            return
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            self._model = genai.GenerativeModel("gemini-2.0-flash")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")

    @property
    def is_configured(self) -> bool:
        self._ensure_model()
        return self._model is not None

    async def classify_intent(self, user_message: str, language: str = "en") -> Dict[str, Any]:
        self._ensure_model()
        if self._model is None:
            return self._fallback_intent(user_message)
        
        system_prompt = (
            "Classify intent: register, check_status, query, help, or other. "
            f"Language: {language}. Respond with JSON."
        )
        try:
            response = self._model.generate_content([system_prompt, user_message])
            text = response.text.strip()
            return json.loads(text) if text.startswith("{") else {"intent": "other", "confidence": 0.5}
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return self._fallback_intent(user_message)

    def _fallback_intent(self, user_message: str) -> Dict[str, Any]:
        lower = user_message.lower()
        if any(kw in lower for kw in ["register", "new", "start"]):
            return {"intent": "register", "confidence": 0.7}
        if any(kw in lower for kw in ["status", "check"]):
            return {"intent": "check_status", "confidence": 0.7}
        return {"intent": "other", "confidence": 0.3}

gemini_llm = GeminiLLM()
