# apps/webhook/whatsapp.py
# WhatsApp Business Cloud API client.
# Handles sending text messages, documents, and downloading media files.

import logging
from typing import Optional, Dict, Any

import httpx

from apps.webhook.config import get_settings

logger = logging.getLogger(__name__)

# Meta Graph API version used for all WhatsApp Cloud API calls.
GRAPH_API_VERSION = "v21.0"


class WhatsAppClient:
    """Thin async wrapper around the WhatsApp Business Cloud API."""

    def __init__(self):
        settings = get_settings()
        self.phone_number_id: str = settings.wa_phone_number_id
        self.access_token: str = settings.wa_access_token
        self.base_url: str = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

    @property
    def is_configured(self) -> bool:
        return bool(self.access_token and self.phone_number_id)

    def _auth_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    # -- Sending messages -------------------------------------------------------

    async def send_text(self, to: str, body: str) -> Dict[str, Any]:
        """Send a plain text message. Returns the API response or a mock dict."""
        if not self.is_configured:
            logger.debug("WA not configured; mocking text send to %s", to)
            return {"mock": True, "to": to, "body": body}

        url = f"{self.base_url}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": body},
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=self._auth_headers())
            response.raise_for_status()
            return response.json()

    async def send_document(self, to: str, document_url: str, caption: str = "", filename: str = "document.pdf") -> Dict[str, Any]:
        """Send a document message (e.g. PDF declaration)."""
        if not self.is_configured:
            return {"mock": True, "to": to, "document_url": document_url}

        url = f"{self.base_url}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "document",
            "document": {
                "link": document_url,
                "caption": caption,
                "filename": filename,
            },
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=self._auth_headers())
            response.raise_for_status()
            return response.json()

    # -- Retrieving media -------------------------------------------------------

    async def get_media_url(self, media_id: str) -> Optional[str]:
        """Given a WhatsApp media ID, retrieve the temporary download URL."""
        if not self.is_configured:
            return None

        url = f"{self.base_url}/{media_id}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=self._auth_headers())
            response.raise_for_status()
            return response.json().get("url")

    async def download_media(self, media_url: str) -> Optional[bytes]:
        """Download media bytes from a WhatsApp-provided temporary URL."""
        if not self.is_configured or not media_url:
            return None

        headers = {"Authorization": f"Bearer {self.access_token}"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(media_url, headers=headers)
            response.raise_for_status()
            return response.content


# Singleton used across the application.
whatsapp_client = WhatsAppClient()
