"""
HTTP client for parser_service integration.
"""

from typing import Any

import httpx

from app.config import settings


class ParserServiceClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.PARSER_SERVICE_URL

    async def start_parse(
        self, keyword: str, depth: int, mode: str
    ) -> dict[str, Any]:
        """
        POST /parse
        Request: { keyword, depth (1-10), mode ("yandex"/"google"/"both") }
        Response: { task_id, message, started_at }
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/parse",
                json={"keyword": keyword, "depth": depth, "mode": mode},
            )
            response.raise_for_status()
            return response.json()

    async def get_results(self, task_id: str) -> dict[str, Any]:
        """
        GET /results/{task_id}
        Response: { status: "running"|"completed"|"failed", links?: list[str], error?: str }
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/results/{task_id}")
            response.raise_for_status()
            return response.json()

    async def health_check(self) -> dict[str, Any]:
        """
        GET /health
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
