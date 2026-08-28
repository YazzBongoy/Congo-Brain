"""Authentication and user management API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from congo_brain.core.config import KEYCLOAK_ENABLED, PUBLIC_REGISTRATION_ENABLED
from congo_brain.core.database import get_db
from congo_brain.core.rbac import Permission, Role, get_all_roles, get_role_permissions
from congo_brain.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    require_permission,
    verify_password,
)
from congo_brain.models.audit import AuditEvent
from congo_brain.models.user import User
from congo_brain.schemas.auth import (
    AdminUserCreate,
    CurrentIdentityOut,
    LoginRequest,
    RoleOut,
    TokenResponse,
    UserCreate,
    UserOut,
    UserUpdate,
)
from congo_brain.services.audit_service import record_audit_event, verify_audit_chain

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _enforce_role_assignment(
    current_user: dict,
    target_role: Role | None,
    *,
    current_target_role: str | None = None,
) -> None:
    """Allow non-admins to manage only strictly less privileged roles."""
    actor_role = str(current_user.get("role", ""))
    if actor_role == Role.ADMIN.value:
        return
    actor_permissions = get_role_permissions(actor_role)
    managed_roles = [role for role in (current_target_role, target_role.value if target_role else None) if role]
    if any(not get_role_permissions(role) < actor_permissions for role in managed_roles):
        raise HTTPException(status_code=403, detail="Role is outside the caller's delegation authority")


def _ensure_local_user_management() -> None:
    """Hide local account lifecycle routes when Keycloak owns identity lifecycle."""
    if KEYCLOAK_ENABLED:
        raise HTTPException(status_code=404, detail="Not found")


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> dict:
    if KEYCLOAK_ENABLED:
        raise HTTPException(status_code=404, detail="Not found")
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(
        {"sub": user.username, "role": user.role, "user_id": user.id, "ministry": user.ministry}
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=UserOut, status_code=201)
def register(body: UserCreate, db: Session = Depends(get_db)) -> User:
    if KEYCLOAK_ENABLED or not PUBLIC_REGISTRATION_ENABLED:
        raise HTTPException(status_code=404, detail="Not found")
    if db.query(User).filter((User.username == body.username) | (User.email == body.email)).first():
        raise HTTPException(status_code=409, detail="Username or email already exists")
    user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
        role=Role.VIEWER.value,
        ministry=body.ministry,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=CurrentIdentityOut)
def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session | None = Depends(get_db),
) -> dict:
    if current_user.get("auth_source") == "keycloak":
        return {
            "subject": current_user["sub"],
            "username": current_user.get("username", ""),
            "email": current_user.get("email", ""),
            "role": current_user["role"],
            "ministry": current_user.get("ministry"),
            "auth_source": "keycloak",
            "local_user_id": None,
        }
    if db is None:
        raise HTTPException(status_code=500, detail="Database session unavailable")
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "subject": current_user["sub"],
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "ministry": user.ministry,
        "auth_source": "local",
        "local_user_id": user.id,
    }


@router.get("/roles", response_model=list[RoleOut])
def list_roles(_user: dict = Depends(require_permission(Permission.USER_READ))) -> list[dict]:
    return get_all_roles()


@router.get("/audit-log")
def list_audit_log(
    limit: int = 100,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_permission(Permission.AUDIT_READ)),
) -> dict:
    safe_limit = max(1, min(limit, 500))
    events = db.query(AuditEvent).order_by(AuditEvent.id.desc()).limit(safe_limit).all()
    chain_events = db.query(AuditEvent).order_by(AuditEvent.id.asc()).all()
    return {
        "count": len(events),
        "chain_valid": verify_audit_chain(chain_events),
        "events": [
            {
                "id": event.id,
                "actor_subject": event.actor_subject,
                "actor_username": event.actor_username,
                "actor_role": event.actor_role,
                "action": event.action,
                "resource_type": event.resource_type,
                "resource_id": event.resource_id,
                "ministry": event.ministry,
                "detail": event.detail,
                "previous_hash": event.previous_hash,
                "event_hash": event.event_hash,
                "created_at": event.created_at,
            }
            for event in events
        ],
    }


@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_permission(Permission.USER_READ)),
) -> list[User]:
    _ensure_local_user_management()
    return db.query(User).all()


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    body: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission(Permission.USER_WRITE)),
) -> User:
    _ensure_local_user_management()
    _enforce_role_assignment(current_user, body.role)
    if db.query(User).filter((User.username == body.username) | (User.email == body.email)).first():
        raise HTTPException(status_code=409, detail="Username or email already exists")
    if body.role == Role.MINISTRY_BUDGET_OFFICER and not body.ministry:
        raise HTTPException(status_code=422, detail="A ministry budget officer must be assigned to a ministry")
    user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
        role=body.role.value,
        ministry=body.ministry,
    )
    db.add(user)
    db.flush()
    db.refresh(user)
    record_audit_event(
        db,
        current_user,
        "user.created",
        "user",
        user.id,
        ministry=user.ministry,
        detail={"username": user.username, "role": user.role},
    )
    return user


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_permission(Permission.USER_READ)),
) -> User:
    _ensure_local_user_management()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    body: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission(Permission.USER_WRITE)),
) -> User:
    _ensure_local_user_management()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    _enforce_role_assignment(current_user, body.role, current_target_role=user.role)
    if body.email is not None:
        existing = db.query(User).filter(User.email == body.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email already in use")
        user.email = body.email
    if body.role is not None:
        user.role = body.role.value
    if body.ministry is not None:
        user.ministry = body.ministry
    if user.role == Role.MINISTRY_BUDGET_OFFICER.value and not user.ministry:
        raise HTTPException(status_code=422, detail="A ministry budget officer must be assigned to a ministry")
    db.flush()
    db.refresh(user)
    record_audit_event(
        db,
        current_user,
        "user.updated",
        "user",
        user.id,
        ministry=user.ministry,
        detail={"username": user.username, "role": user.role},
    )
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission(Permission.USER_DELETE)),
) -> None:
    _ensure_local_user_management()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == Role.ADMIN.value:
        admin_count = db.query(User).filter(User.role == Role.ADMIN.value).count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot delete the last admin user")
    deleted_user_id = user.id
    deleted_username = user.username
    deleted_ministry = user.ministry
    db.delete(user)
    db.flush()
    record_audit_event(
        db,
        current_user,
        "user.deleted",
        "user",
        deleted_user_id,
        ministry=deleted_ministry,
        detail={"username": deleted_username},
    )
