import asyncio
import re
from datetime import datetime, timezone

from events.document_events import DOC_EVENTS
from lib.errors_lib import NotFoundError
from lib.events_lib import app_events
from queues.document_queue import document_queue, queue_document_for_processing
from repositories import document_repository


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
        document_repository.find_many(
            where=where,
            order_by={sort_by: sort_order},
            skip=(page - 1) * limit,
            take=limit,
        ),
        document_repository.count(where),
    )

    return {"data": documents, "meta": {"page": page, "limit": limit, "total": total}}


async def get_document(document_id: str, user_id: str):
    doc = await document_repository.find_active_owned(document_id, user_id)
    if not doc:
        raise NotFoundError("Document not found")
    return doc


async def create_document(user_id: str, title: str, content: str) -> dict:
    doc = await document_repository.create(
        {
            "userId": user_id,
            "title": title,
            "filename": re.sub(r"\s+", "-", title.lower()),
            "content": content,
            "fileSizeBytes": len(content.encode("utf-8")),
            "status": "pending",
        }
    )

    job_id = await queue_document_for_processing(doc.id, user_id)

    app_events.emit(
        DOC_EVENTS["CREATED"],
        {
            "userId": user_id,
            "documentId": doc.id,
            "title": doc.title,
            "fileSizeBytes": doc.fileSizeBytes,
        },
    )

    return {"document": doc, "jobId": job_id}


async def delete_document(document_id: str, user_id: str):
    doc = await document_repository.find_active_owned(document_id, user_id)
    if not doc:
        raise NotFoundError("Document not found")

    deleted = await document_repository.update(
        document_id,
        {"deletedAt": datetime.now(timezone.utc), "deletedBy": user_id},
    )

    app_events.emit(
        DOC_EVENTS["DELETED"],
        {"deletedBy": user_id, "documentId": doc.id, "title": doc.title},
    )

    return deleted


async def get_processing_status(document_id: str, user_id: str) -> dict:
    doc = await document_repository.find_active_owned(document_id, user_id)
    if not doc:
        raise NotFoundError("Document not found")

    jobs = await document_queue.getJobs(["active", "waiting"])
    active_job = next(
        (job for job in jobs if job.data.get("documentId") == document_id), None
    )

    return {
        "status": doc.status,
        "error": doc.error,
        "progress": active_job.progress if active_job else None,
    }
