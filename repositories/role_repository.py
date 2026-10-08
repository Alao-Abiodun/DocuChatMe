from lib.prisma_lib import prisma


async def find_default(client=None):
    db = client or prisma
    return await db.role.find_first(where={"isDefault": True})


async def find_by_name(name: str, client=None):
    db = client or prisma
    return await db.role.find_unique(where={"name": name})


async def list_with_permissions(client=None):
    db = client or prisma
    return await db.role.find_many(
        include={
            "permissions": {"include": {"permission": True}},
            "_count": {"select": {"users": True}},
        }
    )


async def find_user_roles_with_permissions(user_id: str, client=None):
    db = client or prisma
    return await db.userrole.find_many(
        where={"userId": user_id},
        include={
            "role": {"include": {"permissions": {"include": {"permission": True}}}}
        },
    )


async def assign_to_user(user_id: str, role_id: str, assigned_by: str, client=None):
    db = client or prisma
    return await db.userrole.upsert(
        where={"userId_roleId": {"userId": user_id, "roleId": role_id}},
        data={
            "create": {
                "userId": user_id,
                "roleId": role_id,
                "assignedBy": assigned_by,
            },
            "update": {},
        },
    )


async def revoke_from_user(user_id: str, role_id: str, client=None):
    db = client or prisma
    return await db.userrole.delete_many(
        where={"userId": user_id, "roleId": role_id}
    )
