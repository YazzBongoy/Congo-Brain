"""Authentication and password utilities — supports local JWT and Keycloak."""

from datetime import datetime, timedelta, timezone
from functools import lru_cache

import bcrypt
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from congo_brain.core.config import (
    JWT_ALGORITHM, JWT_EXPIRE_MINUTES, SECRET_KEY,
    KEYCLOAK_ENABLED, KEYCLOAK_JWKS_URL, KEYCLOAK_ISSUER, KEYCLOAK_CLIENT_ID,
)
from congo_brain.core.rbac import Permission, has_permission

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


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


# ── Keycloak JWKS ──────────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_keycloak_jwks() -> dict:
    """Fetch Keycloak JWKS (cached)."""
    resp = requests.get(KEYCLOAK_JWKS_URL, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _get_keycloak_signing_key(kid: str) -> str:
    """Extract RSA public key from JWKS by key ID."""
    jwks = _get_keycloak_jwks()
    for key in jwks.get("keys", []):
        if key["kid"] == kid:
            from jose import jwk
            return jwk.construct(key).public_key().decode()
    raise HTTPException(status_code=401, detail="Keycloak signing key not found")


def decode_keycloak_token(token: str) -> dict | None:
    """Validate a Keycloak JWT using JWKS."""
    try:
        unverified = jwt.get_unverified_header(token)
        kid = unverified.get("kid")
        if not kid:
            return None
        signing_key = _get_keycloak_signing_key(kid)
        return jwt.decode(
            token, signing_key, algorithms=["RS256"],
            issuer=KEYCLOAK_ISSUER, audience=KEYCLOAK_CLIENT_ID,
        )
    except Exception:
        return None


# ── Unified auth ───────────────────────────────────────────────

def _try_keycloak(token: str) -> dict | None:
    """Attempt Keycloak validation; returns normalized payload or None."""
    if not KEYCLOAK_ENABLED:
        return None
    payload = decode_keycloak_token(token)
    if payload is None:
        return None
    # Normalize Keycloak claims to our internal format
    roles = payload.get("realm_access", {}).get("roles", [])
    role = "viewer"
    for r in ["admin", "analyst", "viewer"]:
        if r in roles:
            role = r
            break
    return {
        "sub": payload.get("sub"),
        "username": payload.get("preferred_username", payload.get("email", "")),
        "email": payload.get("email", ""),
        "role": role,
        "auth_source": "keycloak",
    }


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Decode JWT and return the current user payload.
    Tries Keycloak first (if enabled), then falls back to local JWT.
    """
    # Try Keycloak
    kc_user = _try_keycloak(token)
    if kc_user is not None:
        return kc_user

    # Fallback to local JWT
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def require_role(*allowed_roles: str) -> dict:
    """Dependency factory that enforces specific user roles."""

    def _check(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.get('role')}' not in {allowed_roles}",
            )
        return current_user

    return _check


def require_permission(permission: Permission) -> dict:
    """Dependency factory that enforces a specific permission."""

    def _check(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "")
        if not has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' required",
            )
        return current_user

    return _check
