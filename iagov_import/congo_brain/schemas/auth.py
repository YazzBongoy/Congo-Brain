"""Auth request/response schemas."""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "viewer"
    ministry: str | None = None


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    ministry: str | None

    model_config = {"from_attributes": True}
