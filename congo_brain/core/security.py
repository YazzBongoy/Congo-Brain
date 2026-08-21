"""Authentication and password utilities — supports local JWT and Keycloak."""

from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Callable

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWKClient
from jwt.exceptions import PyJWTError

from congo_brain.core.config import (
    JWT_ALGORITHM,
    JWT_EXPIRE_MINUTES,
    KEYCLOAK_CLIENT_ID,
    KEYCLOAK_ENABLED,
    KEYCLOAK_ISSUER,
    KEYCLOAK_JWKS_URL,
    SECRET_KEY,
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
    except PyJWTError:
        return None


# ── Keycloak JWKS ──────────────────────────────────────────────


@lru_cache(maxsize=1)
def _get_keycloak_jwk_client() -> PyJWKClient:
    """Create a cached Keycloak JWKS client."""
    return PyJWKClient(KEYCLOAK_JWKS_URL, timeout=10)


def decode_keycloak_token(token: str) -> dict | None:
    """Validate a Keycloak JWT using JWKS."""
    try:
        signing_key = _get_keycloak_jwk_client().get_signing_key_from_jwt(token).key
        return jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=KEYCLOAK_ISSUER,
            audience=KEYCLOAK_CLIENT_ID,
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
    # Normalize Keycloak claims to our internal format. Identity and application
    # authorization claims are mandatory: a cryptographically valid token alone
    # must never acquire a default application role.
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        return None
    realm_access = payload.get("realm_access")
    if not isinstance(realm_access, dict):
        return None
    roles = realm_access.get("roles", [])
    if not isinstance(roles, list):
        return None
    role = next(
        (
            candidate
            for candidate in [
                "admin",
                "national_budget_admin",
                "ministry_budget_officer",
                "project_manager",
                "auditor",
                "executive_viewer",
                "public_viewer",
                "analyst",
                "viewer",
            ]
            if candidate in roles
        ),
        None,
    )
    if role is None:
        return None
    attributes = payload.get("attributes", {})
    if not isinstance(attributes, dict):
        return None
    direct_ministry = payload.get("ministry")
    if direct_ministry is not None:
        if not isinstance(direct_ministry, str):
            return None
        ministry = direct_ministry
    else:
        attribute_ministry = attributes.get("ministry")
        if attribute_ministry is None:
            ministry = None
        elif (
            isinstance(attribute_ministry, list)
            and len(attribute_ministry) == 1
            and isinstance(attribute_ministry[0], str)
        ):
            ministry = attribute_ministry[0]
        else:
            return None
    email = payload.get("email", "")
    preferred_username = payload.get("preferred_username", email)
    if not isinstance(email, str) or not isinstance(preferred_username, str):
        return None
    return {
        "sub": subject,
        "username": preferred_username,
        "email": email,
        "role": role,
        "ministry": ministry,
        "auth_source": "keycloak",
    }


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Decode a token using the single authentication authority configured."""
    if KEYCLOAK_ENABLED:
        kc_user = _try_keycloak(token)
        if kc_user is not None:
            return kc_user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Keycloak token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def require_role(*allowed_roles: str) -> Callable[..., dict]:
    """Dependency factory that enforces specific user roles."""

    def _check(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.get('role')}' not in {allowed_roles}",
            )
        return current_user

    return _check


def require_permission(permission: Permission) -> Callable[..., dict]:
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


def resolve_ministry_scope(current_user: dict, requested_ministry: str | None = None) -> str | None:
    """Resolve a ministry filter and block cross-ministry access for scoped officers."""
    if current_user.get("role") != "ministry_budget_officer":
        return requested_ministry
    assigned = current_user.get("ministry")
    if not assigned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No ministry is assigned to this account")
    if requested_ministry and requested_ministry.casefold() != assigned.casefold():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-ministry access is forbidden")
    return str(assigned)


def enforce_ministry_access(current_user: dict, resource_ministry: str) -> None:
    """Reject access when a ministry officer targets another ministry."""
    resolve_ministry_scope(current_user, resource_ministry)
