from fastapi import FastAPI
from src.media.routes import router

app = FastAPI(
    title="Media Service API"
)

app.include_router(router)