"""Authentication and password utilities."""

from datetime import datetime, timedelta, timezone
from hashlib import sha256

from jose import JWTError, jwt

from congo_brain.core.config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, SECRET_KEY


def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
