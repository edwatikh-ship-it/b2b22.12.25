from typing import Any

from fastapi import APIRouter, Query

router = APIRouter(tags=["Suppliers"])


@router.get("/suppliers/search", summary="Suppliers Search")
async def suppliers_search(
    q: str = Query(..., min_length=1, title="Q"),
    limit: int = Query(20, ge=1, le=200, title="Limit"),
) -> dict[str, Any]:
    # Minimal stable response matching api-contracts.yaml.
    # TODO: replace with real search by DB/index.

    items = [
        {
            "supplierid": 1,
            "name": f"{q.upper()} SUPPLIER",
            "inn": "7707083893",
            "email": "sales@example.com",
            "emails": ["info@example.com", "support@example.com"],
            "urls": [f"https://example.com/search?q={q}"],
            "checko": None,
        },
        {
            "supplierid": 2,
            "name": f"{q.upper()} TRADE",
            "inn": "7813137250",
            "email": "hello@example.org",
            "emails": None,
            "urls": ["https://example.org"],
            "checko": {"source": "mock"},
        },
    ]

    return {
        "items": items[:limit],
        "q": q,
        "limit": limit,
    }
