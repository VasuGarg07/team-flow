import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.realtime import listen_for_events
from app.error_handlers import register_error_handlers
from app.routers import users_router, auth_router, workspaces_router, projects_router, tasks_router, attachments_router, ws_router
from app.security_headers import add_security_headers
from app.config import app_settings
from app.logging_config import setup_logging
from app.request_logging import log_requests
from app.cache import redis_client
from app.database import engine
from app.queue import queue_connection

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("App starting")
    listener_task = asyncio.create_task(listen_for_events())
    yield
    logger.info("App shutting down")
    listener_task.cancel()
    await asyncio.gather(listener_task, return_exceptions=True)
    redis_client.close()
    queue_connection.close()
    engine.dispose()
    logger.info("App stopped")

setup_logging()
app = FastAPI(lifespan=lifespan)

# Middlewares
app.middleware("http")(add_security_headers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.middleware("http")(log_requests)

# Add Routers here
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(workspaces_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(attachments_router)
app.include_router(ws_router)

# Global Error Handlers
register_error_handlers(app)

@app.get("/health")
def health_check():
    return {"status": "ok"}