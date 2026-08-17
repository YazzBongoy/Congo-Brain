"""Role-Based Access Control (RBAC) permissions for Congo-Brain."""

from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class Permission(str, Enum):
    # Budget permissions
    BUDGET_READ = "budget:read"
    BUDGET_WRITE = "budget:write"
    BUDGET_DELETE = "budget:delete"

    # Investment permissions
    INVESTMENT_READ = "investment:read"
    INVESTMENT_WRITE = "investment:write"
    INVESTMENT_OPTIMIZE = "investment:optimize"

    # Security permissions
    SECURITY_READ = "security:read"
    SECURITY_WRITE = "security:write"
    SECURITY_RESOLVE = "security:resolve"

    # Transparency permissions
    TRANSPARENCY_READ = "transparency:read"
    TRANSPARENCY_WRITE = "transparency:write"

    # User management
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"

    # System
    SYSTEM_ADMIN = "system:admin"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {
        Permission.BUDGET_READ, Permission.BUDGET_WRITE, Permission.BUDGET_DELETE,
        Permission.INVESTMENT_READ, Permission.INVESTMENT_WRITE, Permission.INVESTMENT_OPTIMIZE,
        Permission.SECURITY_READ, Permission.SECURITY_WRITE, Permission.SECURITY_RESOLVE,
        Permission.TRANSPARENCY_READ, Permission.TRANSPARENCY_WRITE,
        Permission.USER_READ, Permission.USER_WRITE, Permission.USER_DELETE,
        Permission.SYSTEM_ADMIN,
    },
    Role.ANALYST: {
        Permission.BUDGET_READ, Permission.BUDGET_WRITE,
        Permission.INVESTMENT_READ, Permission.INVESTMENT_WRITE, Permission.INVESTMENT_OPTIMIZE,
        Permission.SECURITY_READ, Permission.SECURITY_WRITE,
        Permission.TRANSPARENCY_READ, Permission.TRANSPARENCY_WRITE,
        Permission.USER_READ,
    },
    Role.VIEWER: {
        Permission.BUDGET_READ,
        Permission.INVESTMENT_READ,
        Permission.SECURITY_READ,
        Permission.TRANSPARENCY_READ,
    },
}


def get_role_permissions(role: str) -> set[Permission]:
    """Get the set of permissions for a given role."""
    try:
        return ROLE_PERMISSIONS[Role(role)]
    except (ValueError, KeyError):
        return set()


def has_permission(role: str, permission: Permission) -> bool:
    """Check if a role has a specific permission."""
    return permission in get_role_permissions(role)


def get_all_roles() -> list[dict]:
    """Return all roles with their permissions (for API docs)."""
    return [
        {
            "role": role.value,
            "permissions": sorted([p.value for p in perms]),
        }
        for role, perms in ROLE_PERMISSIONS.items()
    ]
