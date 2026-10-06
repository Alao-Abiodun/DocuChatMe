from fastapi import APIRouter, Depends

from middlewares.authorize_middleware import require_permission
from lib.prisma_lib import prisma
from lib.events_lib import app_events
from lib.errors_lib import NotFoundError

router = APIRouter(dependencies=[Depends(require_permission("roles:manage"))])


@router.get("/roles")
async def list_roles():
    roles = await prisma.role.find_many(
        include={
            "permissions": {"include": {"permission": True}},
            "_count": {"select": {"users": True}},
        }
    )
    return {
        "success": True,
        "data": [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "isDefault": role.isDefault,
                "userCount": role._count.users,
                "permissions": [rp.permission.name for rp in role.permissions],
            }
            for role in roles
        ],
    }


@router.post("/users/{user_id}/roles")
async def assign_role(user_id: str, body: dict, admin_user: dict = Depends(require_permission("roles:manage"))):
    role_name = body["roleName"]

    user = await prisma.user.find_unique(where={"id": user_id})
    if not user:
        raise NotFoundError("User not found")

    role = await prisma.role.find_unique(where={"name": role_name})
    if not role:
        raise NotFoundError(f"Role '{role_name}' not found")

    await prisma.userrole.upsert(
        where={"userId_roleId": {"userId": user_id, "roleId": role.id}},
        data={
            "create": {"userId": user_id, "roleId": role.id, "assignedBy": admin_user["id"]},
            "update": {},
        },
    )

    app_events.emit("admin:role-assigned", {
        "targetUserId": user_id, "roleName": role_name, "assignedBy": admin_user["id"],
    })

    return {"success": True, "data": {"message": f"Role '{role_name}' assigned to user"}}


@router.delete("/users/{user_id}/roles/{role_name}")
async def revoke_role(user_id: str, role_name: str, admin_user: dict = Depends(require_permission("roles:manage"))):
    role = await prisma.role.find_unique(where={"name": role_name})
    if not role:
        raise NotFoundError("Role not found")

    await prisma.userrole.delete_many(where={"userId": user_id, "roleId": role.id})

    app_events.emit("admin:role-revoked", {
        "targetUserId": user_id, "roleName": role_name, "revokedBy": admin_user["id"],
    })

    return {"success": True, "data": {"message": f"Role '{role_name}' revoked"}}