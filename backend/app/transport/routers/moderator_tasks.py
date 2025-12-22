from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

router = APIRouter(tags=["ModeratorTasks"], prefix="/moderator")


@router.get("/tasks")
async def list_tasks():
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get("/tasks/{taskId}")
async def get_task(task_id: Annotated[str, Path(alias="taskId")]):
    raise HTTPException(status_code=501, detail="Not Implemented")
