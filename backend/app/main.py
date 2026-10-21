from fastapi import FastAPI
from app.routers.users import router as users_router
from .error_handlers import register_error_handlers

app = FastAPI()

# Add Routers here
app.include_router(users_router)

# Global Error Handlers
register_error_handlers(app)

@app.get("/health")
def health_check():
    return {"status": "ok"}