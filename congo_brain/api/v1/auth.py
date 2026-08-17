"""Authentication and user management API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from congo_brain.core.database import get_db
from congo_brain.core.rbac import Permission, get_all_roles
from congo_brain.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    require_permission,
    verify_password,
)
from congo_brain.models.user import User
from congo_brain.schemas.auth import LoginRequest, RoleOut, TokenResponse, UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> dict:
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=UserOut, status_code=201)
def register(body: UserCreate, db: Session = Depends(get_db)) -> User:
    if db.query(User).filter((User.username == body.username) | (User.email == body.email)).first():
        raise HTTPException(status_code=409, detail="Username or email already exists")
    user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
        role=body.role,
        ministry=body.ministry,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/roles", response_model=list[RoleOut])
def list_roles(_user: dict = Depends(require_permission(Permission.USER_READ))) -> list[dict]:
    return get_all_roles()


@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_permission(Permission.USER_READ)),
) -> list[User]:
    return db.query(User).all()


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_permission(Permission.USER_READ)),
) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    body: UserUpdate,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_permission(Permission.USER_WRITE)),
) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if body.email is not None:
        existing = db.query(User).filter(User.email == body.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email already in use")
        user.email = body.email
    if body.role is not None:
        user.role = body.role
    if body.ministry is not None:
        user.ministry = body.ministry
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_permission(Permission.USER_DELETE)),
) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == "admin":
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot delete the last admin user")
    db.delete(user)
    db.commit()
