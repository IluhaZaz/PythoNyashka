from fastapi import FastAPI

from src.bff.routes import profiles_router, router

app = FastAPI(title="BFF API")

app.include_router(router)
app.include_router(profiles_router)
