import json
import logging
import re
from typing import Any, Dict, Iterable, Optional

from apps.webhook.config import get_settings

logger = logging.getLogger(__name__)


class GeminiLLM:
    def __init__(self) -> None:
        self._model = None
        self._initialized = False
        self.api_key = get_settings().gemini_api_key

    def _ensure_model(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set")
            return
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel("gemini-2.0-flash")
        except Exception as exc:
            logger.error("Failed to initialize Gemini: %s", exc)

    @property
    def is_configured(self) -> bool:
        self._ensure_model()
        return self._model is not None

    async def classify_intent(self, user_message: str, language: str = "en") -> Dict[str, Any]:
        self._ensure_model()
        if self._model is None:
            return self._fallback_intent(user_message, language)

        system_prompt = (
            "Classify intent: register, check_status, query, help, or other. "
            f"Language: {language}. Respond with JSON."
        )
        try:
            response = self._model.generate_content([system_prompt, user_message])
            text = response.text.strip()
            if text.startswith("{"):
                return json.loads(text)
        except Exception as exc:
            logger.error("Intent classification failed: %s", exc)
        return self._fallback_intent(user_message, language)

    async def extract_fields(
        self,
        user_message: str,
        fields_needed: Iterable[str],
        existing_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        extracted = self._fallback_extract_fields(user_message)
        if existing_context:
            for key, value in existing_context.items():
                extracted.setdefault(key, value)
        return {field: extracted.get(field) for field in fields_needed}

    async def generate_reply(self, text: str, session: Dict[str, Any], language: str = "en") -> str:
        company = session.get("company_name") or "your MSME"
        if language == "hi":
            return f"Maine '{text}' note kar liya hai. Main {company} ke liye agla compliance step guide kar sakta hoon."
        if language == "te":
            return f"'{text}' ను నేను నమోదు చేశాను. {company} కోసం తదుపరి compliance step లో సహాయం చేయగలను."
        return f"I noted '{text}'. I can guide the next compliance step for {company}."

    def _fallback_intent(self, user_message: str, language: str) -> Dict[str, Any]:
        normalized = user_message.lower().strip()
        if any(token in normalized for token in ["register", "start", "apply", "new"]):
            return {"intent": "register", "language": language, "confidence": 0.7}
        if any(token in normalized for token in ["status", "verify", "passport", "check"]):
            return {"intent": "check_status", "language": language, "confidence": 0.7}
        if any(token in normalized for token in ["help", "support", "guide"]):
            return {"intent": "help", "language": language, "confidence": 0.6}
        if re.search(r"\?$", normalized):
            return {"intent": "query", "language": language, "confidence": 0.5}
        return {"intent": "other", "language": language, "confidence": 0.3}

    def _fallback_extract_fields(self, user_message: str) -> Dict[str, Any]:
        hs_match = re.search(r"\b(\d{4,8})\b", user_message)
        lcv_match = re.search(r"(?:lcv|local content)[^0-9]{0,12}(\d{1,3}(?:\.\d+)?)", user_message, flags=re.IGNORECASE)
        gstin_match = re.search(r"\b[0-9A-Z]{15}\b", user_message)
        dpiit_match = re.search(r"\bDPIIT[- ]?[0-9A-Z-]+\b", user_message, flags=re.IGNORECASE)

        extracted: Dict[str, Any] = {}
        if hs_match:
            extracted["hs_code"] = hs_match.group(1)
        if lcv_match:
            extracted["local_content_pct"] = float(lcv_match.group(1))
        if gstin_match:
            extracted["gstin"] = gstin_match.group(0)
        if dpiit_match:
            extracted["dpiit_no"] = dpiit_match.group(0).replace(" ", "-").upper()
        return extracted


gemini_llm = GeminiLLM()
