from typing import Annotated

from fastapi import APIRouter, Depends, Query

from controllers import document_controller
from middlewares.authorize_middleware import require_permission
from validators.document_validator import CreateDocumentBody, ListDocumentsQuery

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
    return await document_controller.list_documents(query, user)


@router.post("/", status_code=202)
async def create_document(
    body: CreateDocumentBody,
    user: dict = Depends(require_permission("documents:create")),
):
    return await document_controller.create_document(body, user)


@router.get("/{document_id}/processing-status")
async def processing_status(
    document_id: str,
    user: dict = Depends(require_permission("documents:read")),
):
    return await document_controller.processing_status(document_id, user)


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    user: dict = Depends(require_permission("documents:read")),
):
    return await document_controller.get_document(document_id, user)


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    user: dict = Depends(require_permission("documents:delete")),
):
    return await document_controller.delete_document(document_id, user)
