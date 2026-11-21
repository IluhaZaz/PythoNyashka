from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.bff.domain.schemas import ErrorResponse
from src.bff.routes import (
    chats_router,
    matches_router,
    media_router,
    notifications_router,
    profiles_router,
    router,
)
from src.bff.usecase import APIRequestError

app = FastAPI(title="BFF API")

app.include_router(router)
app.include_router(profiles_router)
app.include_router(media_router)
app.include_router(notifications_router)
app.include_router(chats_router)
app.include_router(matches_router)


@app.exception_handler(APIRequestError)
async def api_request_error(_request: Request, exc: APIRequestError) -> JSONResponse:
    headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == HTTPStatus.UNAUTHORIZED else None
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.error).model_dump(),
        headers=headers,
    )
