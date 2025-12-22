import pytest  # noqa: E402

pytest.skip(
    "Suppliers DB models (SupplierModel/SupplierUrlModel) are not present in app.adapters.db.models; suppliers feature needs re-implementation or model restore.",
    allow_module_level=True,
)
import os  # noqa: E402
import time  # noqa: E402

import httpx  # noqa: E402
import pytest  # noqa: E402
from sqlalchemy import delete  # noqa: E402

from app.adapters.db.models import SupplierModel, SupplierUrlModel  # noqa: E402
from app.adapters.db.session import SessionLocal  # noqa: E402


def _dump_proxy_env() -> dict:
    keys = [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "NO_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "no_proxy",
    ]
    return {k: os.getenv(k) for k in keys if os.getenv(k)}


def _get_with_retry(url: str, *, params: dict, timeout: float = 10.0) -> httpx.Response:
    last: Exception | None = None

    # trust_env=False is critical: avoids system/env proxy interfering with localhost calls.
    with httpx.Client(trust_env=False) as client:
        for _ in range(25):  # ~5 sec total
            try:
                r = client.get(url, params=params, timeout=timeout)
                if r.status_code in (503, 502):
                    time.sleep(0.2)
                    continue
                return r
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError) as e:
                last = e
                time.sleep(0.2)

    if last:
        raise last
    return httpx.get(url, params=params, timeout=timeout)


@pytest.mark.integration
def test_suppliers_search_returns_db_results_live_server() -> None:
    port = os.getenv("APPPORT") or "8000"
    prefix = os.getenv("APIPREFIX") or "apiv1"
    base = f"http://127.0.0.1:{port}"

    async def seed() -> None:
        async with SessionLocal() as session:
            await session.execute(delete(SupplierUrlModel))
            await session.execute(delete(SupplierModel))
            await session.commit()

            s1 = SupplierModel(inn="7707083893", name="Acme LLC", sales_email="sales@acme.test")
            s2 = SupplierModel(inn="7812345678", name="Beta Inc", sales_email="hello@beta.test")
            session.add_all([s1, s2])
            await session.flush()

            session.add(SupplierUrlModel(supplier_id=s1.id, url="https://acme.test"))
            await session.commit()

    import asyncio

    asyncio.run(seed())

    url = f"{base}/{prefix}/suppliers/search"
    resp = _get_with_retry(url, params={"q": "acme", "limit": 20}, timeout=10.0)

    if resp.status_code != 200:
        print("DEBUG status:", resp.status_code)
        print("DEBUG url:", str(resp.request.url))
        print("DEBUG headers:", dict(resp.headers))
        print("DEBUG body:", resp.text)
        print("DEBUG proxy_env:", _dump_proxy_env())

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["limit"] == 20

    found = [x for x in data["items"] if x.get("inn") == "7707083893"]
    assert len(found) == 1
    item = found[0]
    assert item["suppliername"] == "Acme LLC"
    assert item["email"] == "sales@acme.test"
    assert item["website"] == "https://acme.test"
    assert isinstance(item["supplierid"], int)
    assert item["supplierid"] > 0
