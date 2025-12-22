import json

import httpx


class CheckoClient:
    def __init__(self, *, api_key: str, base_url: str = "https://api.checko.ru"):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

    async def search_companies(self, *, q: str, limit: int) -> list[dict]:
        url = f"{self._base_url}/v2/search"
        limit = max(1, min(int(limit), 100))

        params = {
            "key": self._api_key,
            "by": "name",
            "obj": "org",
            "query": q,
            "limit": limit,
            "page": 1,
            "active": "true",
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(url, params=params)
            if r.status_code >= 400:
                raise httpx.HTTPStatusError(
                    f"Checko error {r.status_code}: {r.text}", request=r.request, response=r
                )

            if not r.encoding:
                r.encoding = "cp1251"

            payload = json.loads(r.text)

        data = payload.get("data") or {}
        records = data.get("Записи") or []
        return list(records) if isinstance(records, list) else []
