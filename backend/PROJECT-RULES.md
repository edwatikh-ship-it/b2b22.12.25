from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.adapters.db.session import engine
from app.config import settings

from app.transport.routers.health import router as health_router
from app.transport.routers.requests import router as requests_router
from app.transport.routers.attachments import router as attachments_router
from app.transport.routers.auth import router as auth_router
from app.transport.routers.user_blacklist_inn import router as user_blacklist_inn_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="B2B Platform API", version="1.0.0", lifespan=lifespan)

    app.include_router(health_router, prefix=settings.API_PREFIX)
    app.include_router(requests_router, prefix=settings.API_PREFIX)
    app.include_router(attachments_router, prefix=settings.API_PREFIX)
    app.include_router(auth_router, prefix=settings.API_PREFIX)
    app.include_router(user_blacklist_inn_router, prefix=settings.API_PREFIX)

    return app


app = create_app()
---

## Cleanup (anti-trash) rule
- Любые временные правки/костыли (debug prints, закомментированный код, *_tmp.py, одноразовые скрипты, try/except вокруг обязательных импортов, router=None и условные include_router) удаляются в рамках того же коммита/PR, где появились.  
- Если фича описана в SSoT (api-contracts.yaml), то composition root (main.py) импортирует и подключает роутер напрямую; при проблеме приложение должно падать на старте, а не скрывать ошибку.  
- Перед коммитом обязательно: тесты (pytest), smoke-check openapi.json, и git status без неожиданных файлов.

