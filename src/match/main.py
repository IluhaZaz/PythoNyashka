from fastapi import FastAPI
from src.match.routes import router

app = FastAPI(
    title="Match Service API",
    description="Microservice responsible for finding matches and storing their history.",
    version="1.0.0",
)

app.include_router(router)