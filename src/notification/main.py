from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.notification.domain.schemas import ValidationErrorItem, ValidationErrors
from src.notification.routes import router

app = FastAPI(
    title="Notification Service API",
    description="Internal service for creating, listing, and marking notifications as read.",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = ValidationErrors(errors=[
        ValidationErrorItem(
            field=".".join(str(part) for part in error["loc"][1:]) or "body",
            reason=error["msg"],
        )
        for error in exc.errors()
    ])
    return JSONResponse(status_code=422, content=errors.model_dump())


app.include_router(router)
