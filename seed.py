import asyncio
from lib.prisma_lib import prisma


async def seed_rbac():
    permission_defs = [
        {"name": "documents:create", "resource": "documents", "action": "create", "description": "Upload documents"},
        {"name": "documents:read", "resource": "documents", "action": "read", "description": "View documents"},
        {"name": "documents:update", "resource": "documents", "action": "update", "description": "Edit document metadata"},
        {"name": "documents:delete", "resource": "documents", "action": "delete", "description": "Delete documents"},
        {"name": "conversations:create", "resource": "conversations", "action": "create", "description": "Start conversations"},
        {"name": "conversations:read", "resource": "conversations", "action": "read", "description": "View conversations"},
        {"name": "users:read", "resource": "users", "action": "read", "description": "View user list"},
        {"name": "users:manage", "resource": "users", "action": "manage", "description": "Manage user accounts"},
        {"name": "roles:manage", "resource": "roles", "action": "manage", "description": "Manage roles and permissions"},
    ]

    permissions = {}
    for perm in permission_defs:
        permissions[perm["name"]] = await prisma.permission.upsert(
            where={"name": perm["name"]},
            data={"create": perm, "update": {}},
        )

    role_defs = [
        {"name": "admin", "description": "Full system access", "permissions": list(permissions.keys())},
        {
            "name": "member", "description": "Standard user", "is_default": True,
            "permissions": ["documents:create", "documents:read", "documents:update",
                            "conversations:create", "conversations:read"],
        },
        {"name": "viewer", "description": "Read-only access", "permissions": ["documents:read", "conversations:read"]},
    ]

    for role_def in role_defs:
        role = await prisma.role.upsert(
            where={"name": role_def["name"]},
            data={
                "create": {
                    "name": role_def["name"],
                    "description": role_def["description"],
                    "isDefault": role_def.get("is_default", False),
                },
                "update": {},
            },
        )

        for perm_name in role_def["permissions"]:
            await prisma.rolepermission.upsert(
                where={"roleId_permissionId": {"roleId": role.id, "permissionId": permissions[perm_name].id}},
                data={
                    "create": {"roleId": role.id, "permissionId": permissions[perm_name].id},
                    "update": {},
                },
            )

    print("RBAC seeded: 3 roles, 9 permissions")


async def main():
    await prisma.connect()
    try:
        await seed_rbac()
    finally:
        await prisma.disconnect()


if __name__ == "__main__":
    asyncio.run(main())