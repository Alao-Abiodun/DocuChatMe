from lib.prisma_lib import prisma

async def get_user_permissions(user_id: str) -> set[str]:
    user_roles = await prisma.userrole.find_many(
        where={"userId": user_id},
        include={
            "role": {
                "include": {
                    "permissions": {"include": {"permission": True }}
                }
            }
        },
    )

    permissions: set[str] = set()
    for ur in user_roles:
        for rp in ur.role.permissions:
            permissions.add(rp.permission.name)

    return permissions