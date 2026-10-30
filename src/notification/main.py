import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.infrastructure.messaging.kafka.config import KafkaConfig
from src.infrastructure.storage.postgresql.core import DBSession
from src.notification.domain.schemas import ValidationErrorItem, ValidationErrors
from src.notification.infrastructure.messaging.kafka.consumer import NotificationConsumer
from src.notification.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    consumer = NotificationConsumer(KafkaConfig(), DBSession)
    app.state.notification_consumer = consumer
    try:
        await consumer.start()
        task = asyncio.create_task(consumer.run(), name="notification-consumer")
        try:
            yield
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
    finally:
        try:
            await consumer.stop()
        finally:
            await DBSession.kw["bind"].dispose()


app = FastAPI(
    title="Notification Service API",
    description="Internal API for listing and reading notifications created from Kafka events.",
    version="1.0.0",
    lifespan=lifespan,
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
