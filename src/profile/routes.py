import logging

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response

from src.profile import dependencies
from src.profile.domain.schemas import ProfileCreate, ProfileUpdate, ProfileGet
from src.profile.usecase import (
    CreateProfile, UpdateProfile, GetProfile,
    ProfileNotFoundError, ProfileAlreadyExistsError,
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