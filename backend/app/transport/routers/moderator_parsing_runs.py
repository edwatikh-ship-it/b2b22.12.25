from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["ModeratorTasks"])

# Глобальный storage (MVP)
parsing_runs_storage = {
    "mock-run-1": {"id": "mock-run-1", "status": "succeeded", "created_at": "2025-12-21T00:00:00Z"}
}


@router.get("/moderator/parsing-runs", response_model=dict)
async def list_parsing_runs(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    runs = parsing_runs_storage
    if status:
        runs = {k: v for k, v in runs.items() if v.get("status") == status}
    items = list(runs.values())[offset : offset + limit]
    return {
        "items": items,
        "limit": limit,
        "offset": offset,
        "total": len(runs),
    }


@router.get("/moderator/parsing-runs/{run_id}", response_model=dict)
async def get_parsing_run_detail(run_id: str):
    if run_id not in parsing_runs_storage:
        raise HTTPException(status_code=404, detail="Run not found")
    return parsing_runs_storage[run_id]
