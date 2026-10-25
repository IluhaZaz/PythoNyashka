import logging

from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth import dependencies
from src.auth.domain.schemas import RegisterRequest, LoginRequest, RefreshTokenRequest
from src.auth.usecase import Register, Login, InvalidCredentialsError, Logout, InvalidSessionError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

bearer = HTTPBearer(
    auto_error=False,
    bearerFormat="JWT",
)


@router.post("/login")
async def login(
    req: LoginRequest,
    usecase: Login = Depends(dependencies.login_uc),
):
    try:
        return await usecase.execute(req)
    except InvalidCredentialsError:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid credentials"},
        )

@router.post("/logout")
async def logout(
    req: RefreshTokenRequest,
    usecase: Logout = Depends(dependencies.logout_uc),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> Response:
    try:
        if credentials is None:
            raise InvalidSessionError()

        await usecase.execute(
            req=req,
            access_token=credentials.credentials,
        )
    except InvalidSessionError:
        return JSONResponse(
            status_code=401,
            content={"error": "Невалидный токен или сессия"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Response(status_code=204)

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