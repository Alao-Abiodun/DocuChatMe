from fastapi import Depends
from lib.errors_lib import NotFoundError
from services.rbac_service import get_user_permissions
from middlewares.authorize_middleware import require_permission
from lib.prisma_lib import prisma

async def get_document(document_id: str, user: dict = Depends(require_permission("documents:read"))):
    doc = await prisma.document.find_unqiue(where={"id": document_id})

    if not doc:
        raise NotFoundError("Document not found")

    if doc.userId != user["id"]:
        permissions = await get_user_permissions(user["id"])
        if "users:manage" not in permissions:
            raise NotFoundError("Document not found")

        return {"success": True, "data": doc}