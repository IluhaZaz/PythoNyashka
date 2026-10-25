from typing import Literal

from pydantic import BaseModel


class RegisterRequest(BaseModel):
    email: str
    password: str
    profile_id: str


class LoginRequest(BaseModel):
    email: str
    password: str

class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
