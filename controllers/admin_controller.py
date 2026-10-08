from services import admin_service
from validators.admin_validator import AssignRoleBody


async def list_roles() -> dict:
    roles = await admin_service.list_roles()
    return {"success": True, "data": roles}


async def assign_role(user_id: str, body: AssignRoleBody, admin_user: dict) -> dict:
    message = await admin_service.assign_role(
        user_id, body.roleName, admin_user["id"]
    )
    return {"success": True, "data": {"message": message}}


async def revoke_role(user_id: str, role_name: str, admin_user: dict) -> dict:
    message = await admin_service.revoke_role(user_id, role_name, admin_user["id"])
    return {"success": True, "data": {"message": message}}
