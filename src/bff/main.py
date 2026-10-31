from fastapi import FastAPI

from src.bff.routes import media_router, notifications_router, profiles_router, router

app = FastAPI(title="BFF API")

app.include_router(router)
app.include_router(profiles_router)
app.include_router(media_router)
app.include_router(notifications_router)
