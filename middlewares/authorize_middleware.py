from fastapi import HTTPException, Depends
from middlewares.auth_middleware import authenticate
from services.rbac_service import get_user_permissions
from lib.errors_lib import ForbiddenError

def authorize(*allowed_roles: str):
    def check_role(user: dict = Depends(authenticate)) -> dict:
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return check_role

def require_permission(*required_permissions: str):
    async def check_permission(user: dict = Depends(authenticate)) -> dict:
        user_permissions = await get_user_permissions(user["id"])

        missing = [p for p in required_permissions if p not in user_permissions]
        if missing:
            raise ForbiddenError("You do not have the required permission.")

        return user;

    return check_permission