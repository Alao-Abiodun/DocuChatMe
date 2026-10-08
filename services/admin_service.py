from lib.errors_lib import NotFoundError
from lib.events_lib import app_events
from repositories import role_repository, user_repository


async def list_roles() -> list[dict]:
    roles = await role_repository.list_with_permissions()

    return [
        {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "isDefault": role.isDefault,
            "userCount": role._count.users,
            "permissions": [rp.permission.name for rp in role.permissions],
        }
        for role in roles
    ]


async def assign_role(user_id: str, role_name: str, assigned_by: str) -> str:
    if not await user_repository.find_by_id(user_id):
        raise NotFoundError("User not found")

    role = await role_repository.find_by_name(role_name)
    if not role:
        raise NotFoundError(f"Role '{role_name}' not found")

    await role_repository.assign_to_user(user_id, role.id, assigned_by)

    app_events.emit(
        "admin:role-assigned",
        {"targetUserId": user_id, "roleName": role_name, "assignedBy": assigned_by},
    )

    return f"Role '{role_name}' assigned to user"


async def revoke_role(user_id: str, role_name: str, revoked_by: str) -> str:
    role = await role_repository.find_by_name(role_name)
    if not role:
        raise NotFoundError("Role not found")

    await role_repository.revoke_from_user(user_id, role.id)

    app_events.emit(
        "admin:role-revoked",
        {"targetUserId": user_id, "roleName": role_name, "revokedBy": revoked_by},
    )

    return f"Role '{role_name}' revoked"
