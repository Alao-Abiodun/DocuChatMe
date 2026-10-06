from typing import Annotated

from fastapi import APIRouter, Depends, Query

from middlewares.authorize_middleware import require_permission
from services import document_service
from validators.document_validator import ListDocumentsQuery


router = APIRouter()

# Public route - no auth needed
@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/")
async def list_documents(
    query: Annotated[ListDocumentsQuery, Query()],
    user: dict = Depends(require_permission("documents:read")),
):
    return await document_service.list_documents

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    user: dict = Depends(require_permission("documents:read")),
):
    return {"success": True, "data": await document_service.get_document(document_id, user["id"])}

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    user: dict = Depends(require_permission("documents:delete")),
):
    await document_service.delete_document(document_id, user["id"])
    return {"success": True, "data": {"message": "Document deleted"}}


# Protected route = requires valid access token
@router.get("/", dependencies=[Depends(require_permission("document:read"))])
async def list_document():
    print("A")

@router.post("/", dependencies=[Depends(require_permission("documents:create"))])
async def create_document():
    print("F")

@router.delete("/{document_id}", dependencies=[Depends(require_permission("documents:delete"))])
async def delete_document_route(document_id: str):
    print("F")
