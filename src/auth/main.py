from fastapi import Depends, FastAPI

from src.auth.routes import router

app = FastAPI(
    title="Auth Service"
)

app.include_router(router)
