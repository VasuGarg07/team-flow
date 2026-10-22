from fastapi import FastAPI

from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.routers.workspaces import router as workspaces_router
from .error_handlers import register_error_handlers


app = FastAPI()

# Add Routers here
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(workspaces_router)

# Global Error Handlers
register_error_handlers(app)

@app.get("/health")
def health_check():
    return {"status": "ok"}