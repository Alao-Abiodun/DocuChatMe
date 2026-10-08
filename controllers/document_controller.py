from services import document_service
from validators.document_validator import CreateDocumentBody, ListDocumentsQuery


async def list_documents(query: ListDocumentsQuery, user: dict) -> dict:
    result = await document_service.list_documents(
        user["id"],
        page=query.page,
        limit=query.limit,
        status=query.status,
        search=query.search,
        sort_by=query.sort_by,
        sort_order=query.sort_order,
    )
    return {"success": True, **result}


async def get_document(document_id: str, user: dict) -> dict:
    doc = await document_service.get_document(document_id, user["id"])
    return {"success": True, "data": doc}


async def create_document(body: CreateDocumentBody, user: dict) -> dict:
    result = await document_service.create_document(
        user["id"], body.title, body.content
    )
    return {"success": True, "data": result}


async def delete_document(document_id: str, user: dict) -> dict:
    await document_service.delete_document(document_id, user["id"])
    return {"success": True, "data": {"message": "Document deleted"}}


async def processing_status(document_id: str, user: dict) -> dict:
    status = await document_service.get_processing_status(document_id, user["id"])
    return {"success": True, "data": status}
