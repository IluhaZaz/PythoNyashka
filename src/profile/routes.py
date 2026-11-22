import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response

from src.profile import dependencies
from src.profile.domain.schemas import ProfileCreate, ProfileGet, ProfileUpdate
from src.profile.usecase import (
    CreateProfile,
    DeleteProfile,
    GetAvatarUsage,
    GetProfile,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
    UpdateProfile,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post("", status_code=201)
async def create_profile(
    req: ProfileCreate,
    usecase: CreateProfile = Depends(dependencies.create_profile_uc),
):
    try:
        profile_id = await usecase.execute(req)
    except ProfileAlreadyExistsError:
        return JSONResponse(
            status_code=409,
            content={"error": "email already used"},
        )
    return JSONResponse(status_code=201, content={"id": profile_id})


@router.patch("", status_code=204)
async def update_profile(
    req: ProfileUpdate,
    profile_id: str = Query(..., description="ID of the profile to update"),
    usecase: UpdateProfile = Depends(dependencies.update_profile_uc),
) -> Response:
    try:
        await usecase.execute(profile_id, req)
    except ProfileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"error": "Profile not found"},
        )
    return Response(status_code=204)


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(
    profile_id: str,
    usecase: Annotated[DeleteProfile, Depends(dependencies.delete_profile_uc)],
) -> Response:
    await usecase.execute(profile_id)
    return Response(status_code=204)


@router.get("/{profile_id}")
async def get_profile(
    profile_id: str,
    usecase: GetProfile = Depends(dependencies.get_profile_uc),
) -> ProfileGet:
    try:
        profile = await usecase.execute(profile_id)
    except ProfileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"error": "Profile not found"},
        )
    return JSONResponse(status_code=200, content={"profile": profile.model_dump(mode='json')})


@router.get(
    "/avatars/{media_id}",
    operation_id="getAvatarUsage",
    status_code=204,
    response_class=Response,
    responses={404: {"description": "File is not a current profile avatar"}},
)
async def get_avatar_usage(
    media_id: UUID,
    usecase: Annotated[GetAvatarUsage, Depends(dependencies.get_avatar_usage_uc)],
) -> Response:
    return Response(status_code=204 if await usecase.execute(str(media_id)) else 404)
