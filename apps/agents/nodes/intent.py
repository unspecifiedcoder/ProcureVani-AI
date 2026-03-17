# apps/agents/nodes/intent.py
# Intent classification node.

import re
from typing import Dict, Any
from apps.agents.state import MSMEState
from apps.agents.llm import gemini_llm

def detect_language(text: str) -> str:
    if re.search(r"[\u0C00-\u0C7F]", text):
        return "te"
    if re.search(r"[\u0900-\u097F]", text):
        return "hi"
    return "en"

async def intent_node(state: MSMEState) -> Dict[str, Any]:
    user_input = state.get("user_input", "")
    if not user_input:
        return {"intent": "other", "intent_confidence": 0.0}
    
    language = state.get("language") or detect_language(user_input)
    result = await gemini_llm.classify_intent(user_input, language)
    
    return {
        "intent": result.get("intent", "other"),
        "intent_confidence": result.get("confidence", 0.5),
        "language": language,
    }
