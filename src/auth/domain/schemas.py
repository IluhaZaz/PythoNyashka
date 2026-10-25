from pydantic import BaseModel


class RegisterRequest(BaseModel):
    email: str
    password: str
    profile_id: str
