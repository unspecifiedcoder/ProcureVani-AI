from typing import Any


async def transcribe_audio(audio_bytes: bytes) -> str:
    text = audio_bytes.decode("utf-8", errors="ignore").strip()
    if text:
        return text
    return "Voice note received. Please share the product name, HS code, and local content percentage."
