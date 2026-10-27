import logging

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response

from src.profile import dependencies
from src.profile.domain.schemas import ProfileCreate, ProfileUpdate, ProfileGet
from src.profile.usecase import CreateProfile, UpdateProfile, GetProfile, ProfileNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post("", status_code=201)
async def create_profile(
    req: ProfileCreate,
    usecase: CreateProfile = Depends(dependencies.create_profile_uc),
):
    """
    Создает новый профиль.
    Возвращает 201 с {"id": "uuid"}.
    """
    profile_id = await usecase.execute(req)
    return JSONResponse(status_code=201, content={"id": profile_id})


@router.patch("", status_code=204)
async def update_profile(
    req: ProfileUpdate,
    profile_id: str = Query(..., description="ID of the profile to update"),
    usecase: UpdateProfile = Depends(dependencies.update_profile_uc),
) -> Response:
    """
    Обновляет существующий профиль.
    profile_id передается в query параметре.
    Возвращает 204 (No Content) при успехе.
    """
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
):
    """
    Получает профиль по ID.
    profile_id передается в path параметре.
    Возвращает 200 с {"profile": {...}}.
    """
    try:
        profile = await usecase.execute(profile_id)
    except ProfileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"error": "Profile not found"},
        )
    
    # Конвертируем Pydantic модель в dict
    profile_data = profile.model_dump()
    
    # Маппим snake_case -> camelCase для соответствия OpenAPI контракту
    response_data = {
        "id": profile_data["id"],
        "email": profile_data["email"],
        "avatarId": profile_data.get("avatarId"),
        "name": profile_data["name"],
        "surname": profile_data["surname"],
        "age": profile_data["age"],
        "bio": profile_data["bio"],
        "gender": profile_data["gender"],
        "tags": profile_data["tags"],
        "created_at": profile_data["created_at"].isoformat(),
        "updated_at": profile_data["updated_at"].isoformat(),
    }
    
    return JSONResponse(status_code=200, content={"profile": response_data})