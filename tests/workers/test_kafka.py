import json
from types import SimpleNamespace
from unittest.mock import Mock, call, create_autospec
from uuid import UUID

import pytest
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, TopicPartition
from aiokafka.errors import CommitFailedError, KafkaError

from src.auth.infrastructure.messaging.kafka.publisher import NotificationPublisher
from src.infrastructure.messaging.kafka import consumer as kafka_consumer
from src.notification.infrastructure.messaging.kafka.consumer import NotificationConsumer
from tests.helpers import PROFILE_ID

pytestmark = pytest.mark.anyio

PARTITION = TopicPartition("notification.events", 0)
EVENT = {"source": "auth", "profile_id": PROFILE_ID, "text": "Welcome"}


@pytest.fixture
def consumer(monkeypatch):
    backend = create_autospec(AIOKafkaConsumer, instance=True)
    backend.assignment.return_value = {PARTITION}
    factory = Mock(return_value=backend)
    monkeypatch.setattr(kafka_consumer, "AIOKafkaConsumer", factory)
    instance = NotificationConsumer("kafka.test:9092")
    instance.retry_backoff_seconds = 0
    factory.assert_called_once_with(
        PARTITION.topic,
        bootstrap_servers="kafka.test:9092",
        group_id="notification-service",
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )
    return instance, backend


def record(content: bytes, offset: int = 7) -> SimpleNamespace:
    return SimpleNamespace(
        topic=PARTITION.topic,
        partition=PARTITION.partition,
        offset=offset,
        value=content,
    )


async def test_consumer_parses_event_and_commits_next_offset(consumer):
    reader, backend = consumer
    backend.getone.return_value = record(json.dumps(EVENT).encode())

    await reader.start()
    event = await reader.run()
    assert event.profile_id == UUID(PROFILE_ID)
    assert event.text == EVENT["text"]
    assert event.email is None
    backend.commit.assert_not_awaited()
    with pytest.raises(RuntimeError, match="Commit or retry"):
        await reader.run()
    assert await reader.commit() is True
    backend.commit.assert_awaited_once_with({PARTITION: 8})
    with pytest.raises(RuntimeError, match="No Kafka message"):
        await reader.commit()
    await reader.stop()
    backend.start.assert_awaited_once()
    backend.stop.assert_awaited_once()


@pytest.mark.parametrize("invalid", [b"[]", b"{", b'{"profile_id":"invalid"}'])
async def test_consumer_retries_read_errors_and_rewinds_invalid_event(consumer, invalid):
    reader, backend = consumer
    backend.getone.side_effect = [
        KafkaError("temporary read error"),
        record(invalid),
        record(json.dumps(EVENT).encode()),
    ]

    event = await reader.run()

    assert event.text == EVENT["text"]
    assert backend.getone.await_count == 3
    backend.seek.assert_called_once_with(PARTITION, 7)
    backend.commit.assert_not_awaited()


async def test_consumer_retries_commit_on_transient_broker_error(consumer):
    reader, backend = consumer
    backend.getone.return_value = record(json.dumps(EVENT).encode())
    backend.commit.side_effect = [KafkaError("temporary commit error"), None]

    await reader.run()

    assert await reader.commit() is True
    assert backend.commit.await_args_list == [call({PARTITION: 8}), call({PARTITION: 8})]


@pytest.mark.parametrize("retains_partition", [True, False])
async def test_consumer_drops_pending_on_rebalance_and_rewinds_only_owned_partition(
    consumer,
    retains_partition,
):
    reader, backend = consumer
    backend.getone.return_value = record(json.dumps(EVENT).encode())
    backend.commit.side_effect = [CommitFailedError(), None]
    backend.assignment.return_value = {PARTITION} if retains_partition else set()

    await reader.run()
    assert await reader.commit() is False
    assert backend.seek.call_args_list == ([call(PARTITION, 7)] if retains_partition else [])

    await reader.run()
    assert await reader.commit() is True


async def test_notification_publisher_handles_broker_error(caplog):
    producer = create_autospec(AIOKafkaProducer, instance=True)
    producer.send_and_wait.side_effect = KafkaError("test broker unavailable")
    publisher = NotificationPublisher(producer)

    await publisher.publish(PROFILE_ID, "Local test notification")

    producer.send_and_wait.assert_awaited_once()
    assert "Failed to publish Auth notification" in caplog.text
