"""Cliente hacia el Builder (el módulo generador que ejecuta Astro)."""
from typing import Protocol

import httpx

from app.config import Settings
from app.exceptions import ExternalServiceError


class BuilderClient(Protocol):
    def build(self, payload: dict) -> dict: ...


class HttpBuilderClient:
    """Llama al Builder real: POST {BUILDER_URL}/build con el contenido del CMS."""

    def __init__(self, base_url: str, timeout: float):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def build(self, payload: dict) -> dict:
        try:
            response = httpx.post(f"{self.base_url}/build", json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ExternalServiceError(f"El Builder no pudo generar el sitio: {exc}") from exc


class MockBuilderClient:
    """Simula al Builder mientras ese módulo no existe. No genera ningún sitio real."""

    def build(self, payload: dict) -> dict:
        published = [post for post in payload.get("posts", []) if not post.get("draft")]
        return {
            "status": "ok",
            "mock": True,
            "outputDir": "dist/",
            "publishedPosts": len(published),
        }


def get_builder_client(settings: Settings) -> BuilderClient:
    if settings.use_mocks:
        return MockBuilderClient()
    return HttpBuilderClient(settings.builder_url, settings.http_timeout_seconds)
