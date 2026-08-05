"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from congo_brain.core.database import get_db
from congo_brain.core.security import create_access_token, hash_password, verify_password
from congo_brain.models.user import User
from congo_brain.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> dict:
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
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
