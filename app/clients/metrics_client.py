"""Cliente hacia la API de métricas (GraphQL, con MongoDB detrás)."""
from typing import Protocol

import httpx

from app.config import Settings
from app.exceptions import ExternalServiceError

# El CMS pide solo los campos que necesita la interfaz.
METRICS_QUERY = """
query Metricas($blogId: Int!) {
  metricas(blogId: $blogId) {
    visitas
    visitantesUnicos
  }
}
"""


class MetricsClient(Protocol):
    def get_metrics(self, blog_id: int) -> dict: ...


class GraphQLMetricsClient:
    def __init__(self, url: str, timeout: float):
        self.url = url
        self.timeout = timeout

    def get_metrics(self, blog_id: int) -> dict:
        body = {"query": METRICS_QUERY, "variables": {"blogId": blog_id}}
        try:
            response = httpx.post(self.url, json=body, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ExternalServiceError(f"La API de métricas no respondió: {exc}") from exc

        if payload.get("errors"):
            raise ExternalServiceError(f"La API de métricas devolvió errores: {payload['errors']}")
        data = (payload.get("data") or {}).get("metricas")
        if data is None:
            raise ExternalServiceError("La API de métricas no devolvió datos para este blog")
        return data


class MockMetricsClient:
    """Datos de relleno mientras la API de métricas no existe; no son analíticas reales."""

    def get_metrics(self, blog_id: int) -> dict:
        return {"visitas": 100 * blog_id, "visitantesUnicos": 60 * blog_id}


def get_metrics_client(settings: Settings) -> MetricsClient:
    if settings.use_mocks:
        return MockMetricsClient()
    return GraphQLMetricsClient(settings.metrics_url, settings.http_timeout_seconds)
