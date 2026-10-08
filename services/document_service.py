import asyncio
from datetime import datetime, timezone
import re

from lib.errors_lib import NotFoundError
from lib.events_lib import app_events
from lib.prisma_lib import prisma
from events.document_events import DOC_EVENTS


async def list_documents(
    user_id: str,
    page: int,
    limit: int,
    status: str | None = None,
    search: str | None = None,
    sort_by: str = "createdAt",
    sort_order: str = "desc",
) -> dict:
    where: dict = {"userId": user_id, "deletedAt": None}

    if status:
        where["status"] = status

    if search:
        where["OR"] = [
            {"title": {"contains": search, "mode": "insensitive"}},
            {"description": {"contains": search, "mode": "insensitive"}},
        ]

    documents, total = await asyncio.gather(
        prisma.document.find_many(
            where=where,
            order={sort_by: sort_order},
            skip=(page - 1) * limit,
            take=limit,
        ),
        prisma.document.count(where=where),
    )

    return {"data": documents, "meta": {"page": page, "limit": limit, "total": total}}


async def get_document(document_id: str, user_id: str):
    doc = await prisma.document.find_first(
        where={"id": document_id, "userId": user_id, "deletedAt": None}
    )
    if not doc:
        raise NotFoundError("Document not found")
    return doc


from queues.document_queue import queue_document_for_processing


async def create_document(user_id: str, title: str, content: str) -> dict:
    doc = await prisma.document.create(
        data={
            "userId": user_id,
            "title": title,
            "filename": re.sub(r"\s+", "-", title.lower()),
            "content": content,
            "fileSizeBytes": len(content.encode("utf-8")),
            "status": "pending",
        }
    )

    job_id = await queue_document_for_processing(doc.id, user_id)

    app_events.emit(DOC_EVENTS["CREATED"], {
        "userId": user_id,
        "documentId": doc.id,
        "title": doc.title,
        "fileSizeBytes": doc.fileSizeBytes,
    })

    return {"document": doc, "jobId": job_id}

async def delete_document(document_id: str, user_id: str):
    doc = await prisma.document.find_unique(where={"id": document_id})

    if not doc or doc.deletedAt:
        raise NotFoundError("Document not found!")
    
    if doc.userId != user_id:
        raise NotFoundError("Document not found!")

    deleted = await prisma.document.update(
        where={"id": document_id},
        data={"deletedAt": datetime.now(timezone.utc), "deletedBy": user_id}
    )

    app_events.emit(DOC_EVENTS["DELETED"], {
        "deletedBy": user_id,
        "documentId": doc.id,
        "title": doc.title
    })
    return deleted