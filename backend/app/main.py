from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.adapters.db.session import engine
from app.transport.routers.attachments import router as attachments_router
from app.transport.routers.auth import router as auth_router
from app.transport.routers.health import router as health_router
from app.transport.routers.moderator_blacklist_domains import (
    router as moderator_blacklist_domains_router,
)
from app.transport.routers.moderator_domain_decision import (
    router as moderator_domain_decision_router,
)
from app.transport.routers.moderator_parsing_runs import (
    router as moderator_parsing_runs_router,
)
from app.transport.routers.moderator_pending_domains import (
    router as moderator_pending_domains_router,
)
from app.transport.routers.moderator_suppliers import router as moderator_suppliers_router
from app.transport.routers.moderator_tasks import router as moderator_tasks_router
from app.transport.routers.requests import router as requests_router
from app.transport.routers.suppliers import router as suppliers_router
from app.transport.routers.user_blacklist_inn import router as user_blacklist_inn_router
from app.transport.routers.user_messaging import router as user_messaging_router
from app.transport.routers.user_upload_and_create import router as user_upload_and_create_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="B2B Platform API", version="1.0.0", lifespan=lifespan)

    app.include_router(health_router)
    app.include_router(requests_router)
    app.include_router(user_upload_and_create_router)
    app.include_router(user_messaging_router)
    app.include_router(attachments_router)
    app.include_router(auth_router)
    app.include_router(suppliers_router)
    app.include_router(moderator_tasks_router)
    app.include_router(moderator_domain_decision_router)
    app.include_router(moderator_suppliers_router)
    app.include_router(moderator_blacklist_domains_router)
    app.include_router(user_blacklist_inn_router)
    app.include_router(moderator_pending_domains_router)
    app.include_router(moderator_parsing_runs_router)

    return app


app = create_app()
