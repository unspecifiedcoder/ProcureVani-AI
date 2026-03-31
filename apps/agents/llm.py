import re
from typing import Any

from apps.webhook.config import get_settings


class GeminiLLM:
    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.gemini_api_key

    async def classify_intent(self, text: str, language: str = "en") -> dict[str, Any]:
        normalized = text.lower().strip()
        if any(token in normalized for token in ["register", "start", "apply", "new"]):
            return {"intent": "register", "language": language}
        if any(token in normalized for token in ["status", "verify", "passport"]):
            return {"intent": "check_status", "language": language}
        if any(token in normalized for token in ["help", "support", "guide"]):
            return {"intent": "help", "language": language}
        if re.search(r"\?$", normalized):
            return {"intent": "query", "language": language}
        return {"intent": "other", "language": language}

    async def generate_reply(self, text: str, session: dict[str, Any], language: str = "en") -> str:
        company = session.get("company_name") or "your MSME"
        if language == "hi":
            return f"Maine '{text}' note kar liya hai. Main {company} ke liye agla compliance step guide kar sakta hoon."
        if language == "te":
            return f"'{text}' ను నేను నమోదు చేశాను. {company} కోసం తదుపరి compliance step లో సహాయం చేయగలను."
        return f"I noted '{text}'. I can guide the next compliance step for {company}."


gemini_llm = GeminiLLM()
