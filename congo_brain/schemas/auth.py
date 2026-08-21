"""Auth request/response schemas."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from congo_brain.core.rbac import Role


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    ministry: str | None = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    role: Role | None = None
    ministry: str | None = None


class AdminUserCreate(UserCreate):
    """Privileged user-provisioning input, accepted only by administrators."""

    role: Role


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    ministry: str | None

    model_config = {"from_attributes": True}


class CurrentIdentityOut(BaseModel):
    subject: str
    username: str
    email: str
    role: str
    ministry: str | None = None
    auth_source: str
    local_user_id: int | None = None


class RoleOut(BaseModel):
    role: str
    permissions: list[str]
