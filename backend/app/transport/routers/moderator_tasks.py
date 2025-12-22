from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["ModeratorTasks"], prefix="/moderator")


@router.get("/tasks")
async def list_tasks():
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    raise HTTPException(status_code=501, detail="Not Implemented")
