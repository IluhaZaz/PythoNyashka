from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response

from src.notification import dependencies
from src.notification.domain.schemas import (
    Error,
    NotificationsGetResponse,
    ValidationErrors,
)
from src.notification.usecase import (
    GetNotifications,
    NotificationNotFoundError,
    ReadNotification,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "/{profile_id}",
    operation_id="getNotifications",
    response_model=NotificationsGetResponse,
    responses={
        422: {"model": ValidationErrors, "description": "Invalid request parameters or body"},
    },
)
async def get_notifications(
    profile_id: UUID,
    usecase: Annotated[GetNotifications, Depends(dependencies.get_notifications_uc)],
    limit: Annotated[int | None, Query(
        description="Maximum number of notifications to return.",
    )] = 10,
    offset: Annotated[int, Query(description="Number of notifications to skip.")] = 0,
) -> NotificationsGetResponse:
    notifications = await usecase.execute(str(profile_id), limit=limit, offset=offset)
    return NotificationsGetResponse(notifications=notifications)


@router.post(
    "/{notification_id}/read",
    status_code=204,
    operation_id="readNotification",
    response_class=Response,
    responses={
        404: {"model": Error, "description": "Notification not found for this profile"},
        422: {"model": ValidationErrors, "description": "Invalid request parameters or body"},
    },
)
async def read_notification(
    notification_id: UUID,
    profile_id: Annotated[UUID, Query(
        description="Current profile ID supplied by the BFF from the validated JWT.",
    )],
    usecase: Annotated[ReadNotification, Depends(dependencies.read_notification_uc)],
) -> Response:
    try:
        await usecase.execute(notification_id=str(notification_id), profile_id=str(profile_id))
    except NotificationNotFoundError:
        return JSONResponse(
            status_code=404,
            content=Error(error="Notification not found for this profile").model_dump(),
        )
    return Response(status_code=204)
