from fastapi import FastAPI

from .error_handlers import register_error_handlers
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.routers.workspaces import router as workspaces_router
from app.routers.projects import router as projects_router
from app.routers.tasks import router as tasks_router


app = FastAPI()

# Add Routers here
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(workspaces_router)
app.include_router(projects_router)
app.include_router(tasks_router)

# Global Error Handlers
register_error_handlers(app)

@app.get("/health")
def health_check():
    return {"status": "ok"}