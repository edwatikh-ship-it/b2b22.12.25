"""In-memory storage for parsing runs (MVP; no DB yet)."""

import uuid
from typing import Any

_runs: dict[str, dict[str, Any]] = {}


def create_run(request_id: int, key_ids: list[int]) -> str:
    run_id = str(uuid.uuid4())
    _runs[run_id] = {
        "requestId": request_id,
        "status": "queued",
        "keys": {
            kid: {"status": "succeeded", "items": [{"domain": f"test{kid}.ru"}], "error": None}
            for kid in key_ids
        },
    }
    return run_id


def get_run(run_id: str) -> dict[str, Any] | None:
    return _runs.get(run_id)


def get_latest_run_by_request(request_id: int) -> tuple[str, dict[str, Any]] | None:
    candidates = [(rid, r) for rid, r in _runs.items() if r["requestId"] == request_id]
    return candidates[-1] if candidates else None


def update_run_status(run_id: str, status: str) -> None:
    if run_id in _runs:
        _runs[run_id]["status"] = status


def update_key_status(
    run_id: str, key_id: int, status: str, items: list[dict], error: str | None = None
) -> None:
    if run_id in _runs and key_id in _runs[run_id]["keys"]:
        _runs[run_id]["keys"][key_id] = {"status": status, "items": items, "error": error}


# SEED TEST DATA ON IMPORT (survives reload)
if not _runs:
    print("DEBUG: Seeding parsing_storage with test data")
    create_run(555, [1, 2])
    create_run(556, [3, 4])

parsing_storage = type(
    "ParsingStorage",
    (),
    {
        "create_run": staticmethod(create_run),
        "get_run": staticmethod(get_run),
        "get_latest_run_by_request": staticmethod(get_latest_run_by_request),
        "update_run_status": staticmethod(update_run_status),
        "update_key_status": staticmethod(update_key_status),
        "_runs": _runs,
    },
)()
