from fastapi import FastAPI
import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app.realtime import listen_for_events
from app.error_handlers import register_error_handlers
from app.routers import users_router, auth_router, workspaces_router, projects_router, tasks_router, attachments_router, ws_router

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    listener_task = asyncio.create_task(listen_for_events())
    yield
    listener_task.cancel()

app = FastAPI(lifespan=lifespan)

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