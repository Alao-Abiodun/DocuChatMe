from fastapi import APIRouter, Depends

from controllers import admin_controller
from middlewares.authorize_middleware import require_permission
from validators.admin_validator import AssignRoleBody

router = APIRouter(dependencies=[Depends(require_permission("roles:manage"))])


@router.get("/roles")
async def list_roles():
    return await admin_controller.list_roles()


@router.post("/users/{user_id}/roles")
async def assign_role(
    user_id: str,
    body: AssignRoleBody,
    admin_user: dict = Depends(require_permission("roles:manage")),
):
    return await admin_controller.assign_role(user_id, body, admin_user)


@router.delete("/users/{user_id}/roles/{role_name}")
async def revoke_role(
    user_id: str,
    role_name: str,
    admin_user: dict = Depends(require_permission("roles:manage")),
):
    return await admin_controller.revoke_role(user_id, role_name, admin_user)
