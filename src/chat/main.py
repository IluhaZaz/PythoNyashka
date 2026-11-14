from fastapi import FastAPI

from src.chat.routes import router

app = FastAPI(
    title="Chat Service",
    description="Microservice responsible for storing, managing, and providing chats data.",
    version="1.0.0",
)

app.include_router(router)
