import asyncio
from unittest.mock import Mock, call, create_autospec

import pytest
from tenacity import wait_none

from src.infrastructure.messaging.kafka.events import NotificationEvent
from src.notification.infrastructure.messaging.kafka.consumer import NotificationConsumer
from src.notification.infrastructure.messaging.smtp.sender import SMTPSender
from src.notification.infrastructure.storage.postgresql.repository import NotificationRepository
from src.notification.usecase import CreateNotification
from tests.helpers import PROFILE_ID

pytestmark = pytest.mark.anyio


@pytest.fixture
def consumer():
    instance = create_autospec(NotificationConsumer, instance=True)
    instance.processing_timeout_seconds = 2
    instance.retry_backoff_seconds = 0
    return instance


@pytest.mark.parametrize(
    ("email", "send_error", "expected_calls", "sent"),
    [
        (None, None, 0, False),
        ("recipient@example.com", None, 1, True),
        ("recipient@example.com", OSError("SMTP unavailable"), 3, False),
    ],
    ids=["no-email", "sent", "smtp-failed"],
)
async def test_worker_saves_notification_and_commits_after_email_handling(
    db_sessions,
    consumer,
    monkeypatch,
    email,
    send_error,
    expected_calls,
    sent,
):
    event = NotificationEvent(source="auth", profile_id=PROFILE_ID, text="Welcome", email=email)
    consumer.run.side_effect = [event, asyncio.CancelledError()]
    sender = create_autospec(SMTPSender, instance=True)
    sender.send.side_effect = send_error
    monkeypatch.setattr(
        CreateNotification,
        "_send_email",
        CreateNotification._send_email.retry_with(wait=wait_none()),
    )

    async with db_sessions() as session:
        repo = NotificationRepository(session)

        async def commit_offset():
            assert not session.in_transaction(), "Commit the database transaction before Kafka"
            async with db_sessions() as reader:
                (notification,) = await NotificationRepository(reader).get_by_profile(PROFILE_ID)
                assert notification.text == event.text
                assert notification.is_read is False
                assert notification.is_sent is sent
            return True

        consumer.commit.side_effect = commit_offset
        with pytest.raises(asyncio.CancelledError):
            await CreateNotification(consumer, repo, sender).execute()

    consumer.commit.assert_awaited_once()
    consumer.retry.assert_not_called()
    assert sender.send.await_count == expected_calls
    if email is not None:
        sender.send.assert_awaited_with(email, event.subject, event.text)


async def test_worker_retries_event_without_committing_offset_on_database_failure(consumer):
    event = NotificationEvent(source="auth", profile_id=PROFILE_ID, text="Welcome")
    consumer.run.side_effect = [event, asyncio.CancelledError()]
    repo = create_autospec(NotificationRepository, instance=True)
    repo.create.side_effect = OSError("Test database error")
    sender = create_autospec(SMTPSender, instance=True)

    with pytest.raises(asyncio.CancelledError):
        await CreateNotification(consumer, repo, sender).execute()

    repo.create.assert_awaited_once_with(profile_id=PROFILE_ID, text=event.text)
    consumer.retry.assert_called_once()
    consumer.commit.assert_not_awaited()
    sender.send.assert_not_awaited()


async def test_worker_acknowledges_redelivery_only_after_a_successful_write(consumer):
    event = NotificationEvent(source="auth", profile_id=PROFILE_ID, text="Welcome")
    consumer.run.side_effect = [event, event, asyncio.CancelledError()]
    consumer.commit.return_value = True
    repo = create_autospec(NotificationRepository, instance=True)
    repo.create.side_effect = [OSError("Temporary storage failure"), "notification-id"]
    sender = create_autospec(SMTPSender, instance=True)
    operations = Mock()
    operations.attach_mock(repo.create, "save")
    operations.attach_mock(consumer.retry, "retry")
    operations.attach_mock(consumer.commit, "acknowledge")

    with pytest.raises(asyncio.CancelledError):
        await CreateNotification(consumer, repo, sender).execute()

    save = call.save(profile_id=PROFILE_ID, text=event.text)
    assert operations.mock_calls == [save, call.retry(), save, call.acknowledge()]
    sender.send.assert_not_awaited()
