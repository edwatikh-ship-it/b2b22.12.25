from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
import asyncio
from datetime import datetime
from src.parser import SearchParser
from src.utils import save_links, setup_logging
from src.config import settings

app = FastAPI(title="Search Parser API", version="1.0.0")

class ParseRequest(BaseModel):
    keyword: str = Field(..., description="Ключевое слово для поиска")
    depth: int = Field(3, ge=1, le=10, description="Глубина поиска (1-10 страниц)")
    mode: Literal["yandex", "google", "both"] = Field("both", description="Режим работы")
    output_file: Optional[str] = Field(None, description="Имя файла для сохранения")

class ParseResponse(BaseModel):
    task_id: str
    message: str
    started_at: datetime

class ParseResult(BaseModel):
    links_count: int
    links: list[str]
    keyword: str
    depth: int
    mode: str

results_storage = {}

setup_logging(settings.log_file)

async def parse_task(task_id: str, request: ParseRequest):
    """Фоновая задача парсинга"""
    try:
        parser = SearchParser()
        links = await parser.parse(request.keyword, request.depth, request.mode)
        
        output_file = request.output_file or f"results_{task_id}.txt"
        save_links(links, output_file)
        
        results_storage[task_id] = {
            "status": "completed",
            "links_count": len(links),
            "links": list(links),
            "keyword": request.keyword,
            "depth": request.depth,
            "mode": request.mode,
            "output_file": output_file
        }
    except Exception as e:
        results_storage[task_id] = {
            "status": "failed",
            "error": str(e)
        }

@app.post("/parse", response_model=ParseResponse)
async def start_parse(request: ParseRequest, background_tasks: BackgroundTasks):
    """
    Запуск парсинга в фоновом режиме
    
    Пример:
        POST /parse
        {
            "keyword": "кирпич",
            "depth": 3,
            "mode": "both"
        }
    """
    task_id = f"{request.keyword}_{datetime.now().timestamp()}"
    
    background_tasks.add_task(parse_task, task_id, request)
    
    results_storage[task_id] = {"status": "running"}
    
    return ParseResponse(
        task_id=task_id,
        message="Парсинг запущен в фоновом режиме",
        started_at=datetime.now()
    )

@app.get("/results/{task_id}")
async def get_results(task_id: str):
    """Получение результатов парсинга"""
    if task_id not in results_storage:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    result = results_storage[task_id]
    
    if result["status"] == "running":
        return {"status": "running", "message": "Парсинг в процессе..."}
    
    return result

@app.get("/health")
async def health():
    """Проверка работоспособности"""
    return {"status": "ok", "cdp_endpoint": settings.cdp_endpoint}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
