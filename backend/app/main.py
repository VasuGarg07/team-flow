from fastapi import FastAPI
from app.routers.users import router as users_router


app = FastAPI()

# Add Routers here
app.include_router(users_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}