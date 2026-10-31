from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.infrastructure.messaging.kafka.publisher import NotificationPublisher
from src.auth.routes import router
from src.infrastructure.messaging.kafka.config import KafkaConfig
from src.infrastructure.messaging.kafka.producer import create_producer
from src.infrastructure.storage.postgresql.core import DBSession


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    config = KafkaConfig()
    producer = create_producer(
        bootstrap_servers=config.bootstrap_servers,
        request_timeout_ms=max(1, int(config.publish_timeout_seconds * 1000)),
    )
    app.state.notification_publisher = NotificationPublisher(producer, config)
    try:
        await producer.start()
        yield
    finally:
        try:
            await producer.stop()
        finally:
            await DBSession.kw["bind"].dispose()

app = FastAPI(
    title="Auth Service",
    lifespan=lifespan,
)

app.include_router(router)
