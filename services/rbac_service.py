from repositories import role_repository


async def get_user_permissions(user_id: str) -> set[str]:
    user_roles = await role_repository.find_user_roles_with_permissions(user_id)

    permissions: set[str] = set()
    for user_role in user_roles:
        for role_permission in user_role.role.permissions:
            permissions.add(role_permission.permission.name)

    return permissions
