from fastapi import FastAPI

from src.profile.routes import router

app = FastAPI(
    title="Profile Service",
    description="Microservice responsible for storing, managing, and providing profile data",
    version="1.0.0",
)

app.include_router(router)