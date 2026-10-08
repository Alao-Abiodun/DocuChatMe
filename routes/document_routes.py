from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from middlewares.authorize_middleware import require_permission
from services import document_service
from validators.document_validator import ListDocumentsQuery

from lib.errors_lib import NotFoundError

from queues.document_queue import document_queue

from lib.prisma_lib import prisma


router = APIRouter()

class CreateDocumentBody(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)

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

@router.post("/", status_code=202)
async def create_document(
    body: CreateDocumentBody,
    user: dict = Depends(require_permission("documents:create"))
):
    result = await document_service.create_document(user["id"], body.title, body.content)
    return {"success": True, "data": result}

@router.delete("/{document_id}", dependencies=[Depends(require_permission("documents:delete"))])
async def delete_document_route(document_id: str):
    print("F")

@router.get("/{document_id}/processing-status")
async def processing_status(
    document_id: str,
    user: dict = Depends(require_permission("documents:read")),
):
    doc = await prisma.document.find_first(
        where={"id": document_id, "userId": user["id"], "deletedAt": None}
    )
    if not doc:
        raise NotFoundError("Document not found")

    jobs = await document_queue.getJobs(["active", "waiting"])
    active_job = next(
        (j for j in jobs if j.data.get("documentId") == document_id),
        None,
    )

    return {
        "success": True,
        "data": {
            "status": doc.status,
            "error": doc.error,
            "progress": active_job.progress if active_job else None,
        },
    }