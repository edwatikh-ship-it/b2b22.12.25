import asyncio
import sys

# CRITICAL: Set event loop policy BEFORE any other imports
# This must be the very first thing to avoid NotImplementedError on Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
from src.parser import SearchParser
from src.utils import save_links, setup_logging
from src.config import settings

app = FastAPI(title="Search Parser API", version="1.0.0")

# TEMPORARILY DISABLED MIDDLEWARE FOR DEBUGGING
# Add middleware to log all requests
# @app.middleware("http")
# async def log_requests(request, call_next):
#     import logging
#     logger = logging.getLogger(__name__)
#     logger.info(f"Request: {request.method} {request.url.path}")
#     try:
#         response = await call_next(request)
#         logger.info(f"Response: {response.status_code} for {request.method} {request.url.path}")
#         return response
#     except Exception as e:
#         logger.error(f"Exception in middleware: {e}", exc_info=True)
#         # Return 500 instead of raising to avoid FastAPI's default 503
#         from fastapi.responses import JSONResponse
#         return JSONResponse(
#             status_code=500,
#             content={"detail": f"Middleware error: {str(e)}"}
#         )

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
    parser = None
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Starting parse_task for task_id={task_id}, keyword={request.keyword}")
        
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
        logger.info(f"Parse task completed: task_id={task_id}, links_count={len(links)}")
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        error_msg = str(e)
        error_traceback = traceback.format_exc()
        logger.error(f"Parse task failed: task_id={task_id}, error={error_msg}\n{traceback.format_exc()}")
        
        results_storage[task_id] = {
            "status": "failed",
            "error": error_msg,
            "error_traceback": error_traceback
        }
    finally:
        # Clean up parser connection
        if parser:
            try:
                await parser.close()
            except Exception as cleanup_err:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error during parser cleanup: {cleanup_err}")

@app.post("/parse", response_model=ParseResponse)
async def start_parse(request: ParseRequest):
    """
    Запуск парсинга
    
    Возвращает task_id сразу, парсинг запускается в фоне через threading.
    
    Пример:
        POST /parse
        {
            "keyword": "кирпич",
            "depth": 3,
            "mode": "both"
        }
    """
    import logging
    import traceback
    from fastapi.responses import JSONResponse
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[PARSE] Starting parse request: keyword={request.keyword}, depth={request.depth}, mode={request.mode}")
        
        task_id = f"{request.keyword}_{datetime.now().timestamp()}"
        
        # Mark as running immediately
        results_storage[task_id] = {"status": "running"}
        
        logger.info(f"[PARSE] Created task_id={task_id}")
        
        # RADICAL FIX: Use threading instead of asyncio to avoid event loop issues
        import threading
        
        def run_parse_task():
            """Wrapper function to run parse_task in a new event loop"""
            try:
                logger.info(f"[PARSE] Thread started for task_id={task_id}")
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(parse_task(task_id, request))
                loop.close()
                logger.info(f"[PARSE] Thread completed for task_id={task_id}")
            except Exception as e:
                logger.error(f"[PARSE] Thread error in parse_task: {e}", exc_info=True)
                results_storage[task_id] = {
                    "status": "failed",
                    "error": f"Thread execution error: {str(e)}"
                }
        
        thread = threading.Thread(target=run_parse_task, daemon=True)
        thread.start()
        logger.info(f"[PARSE] Started parse task thread for task_id={task_id}")
        
        response = ParseResponse(
            task_id=task_id,
            message="Парсинг запущен в фоновом режиме",
            started_at=datetime.now()
        )
        logger.info(f"[PARSE] Returning response for task_id={task_id}")
        return response
        
    except Exception as e:
        logger.error(f"[PARSE] CRITICAL ERROR in start_parse endpoint: {e}", exc_info=True)
        error_details = traceback.format_exc()
        logger.error(f"[PARSE] Traceback: {error_details}")
        
        # Return 500 with detailed error
        return JSONResponse(
            status_code=500,
            content={
                "detail": f"Internal server error: {str(e)}",
                "traceback": error_details
            }
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
    # Simplified health check - just return OK
    # CDP availability will be checked when parsing starts
    # This avoids blocking issues with async subprocess on Windows
    return {
        "status": "ok",
        "cdp_endpoint": settings.cdp_endpoint,
        "cdp_available": None,  # Don't check here - let parse_task handle it
        "cdp_error": None
    }

@app.post("/parse-simple")
async def parse_simple():
    """Minimal test endpoint"""
    return {"status": "ok", "message": "Simple endpoint works"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
