import logging

from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse

from src.auth import dependencies
from src.auth.domain.schemas import RegisterRequest
from src.auth.usecase import Register

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login():
    pass

@router.post("/logout")
async def logout():
    pass

@router.post("/register")
async def register(
    usecase: Register = Depends(dependencies.register_uc),
    req: RegisterRequest = Body(media_type="application/json")
):
    id_ = await usecase.execute(req)
    return JSONResponse(status_code=201, content={"user_id": id_})

@router.post("/refresh")
async def refresh_token():
    pass

@router.post("/password/reset")
async def reset_password():
    pass