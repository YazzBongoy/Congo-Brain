"""Auth request/response schemas."""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "viewer"
    ministry: str | None = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    role: str | None = None
    ministry: str | None = None


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    ministry: str | None

    model_config = {"from_attributes": True}


class RoleOut(BaseModel):
    role: str
    permissions: list[str]
