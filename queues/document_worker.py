from datetime import datetime, timezone

from bullmq import Job, Worker

from lib.chunker_lib import estimate_tokens, split_into_chunks
from lib.events_lib import app_events
from lib.transaction_lib import transaction
from queues.connection_queue import REDIS_URL
from queues.dead_letter_queue import dead_letter_queue
from queues.document_queue import MAX_ATTEMPTS
from repositories import document_repository


async def process_document(job: Job, token: str) -> dict:
    document_id = job.data["documentId"]
    user_id = job.data["userId"]
    print(f"Processing document {document_id} (attempt {job.attemptsMade + 1})")

    # Change 1: a missing or deleted document is a PERMANENT failure.
    # Retrying won't fix it, so finish the job quietly.
    doc = await document_repository.find_by_id(document_id)
    if not doc or doc.deletedAt:
        print(f"Document {document_id} not found or deleted, skipping")
        return {"success": False, "skipped": True}

    try:
        await document_repository.update(document_id, {"status": "processing"})
        await job.updateProgress(10)

        # Split into chunks
        chunks = split_into_chunks(doc.content or "", 500)
        await job.updateProgress(40)

        # Store chunks + mark ready, all-or-nothing
        async with transaction() as tx:
            # Idempotent: wipe chunks from any previous attempt first
            await document_repository.delete_chunks(document_id, client=tx)

            await document_repository.create_chunks(
                [
                    {
                        "documentId": document_id,
                        "index": index,
                        "content": text,
                        "tokenCount": estimate_tokens(text),
                    }
                    for index, text in enumerate(chunks)
                ],
                client=tx,
            )

            await document_repository.update(
                document_id,
                {"status": "ready", "chunkCount": len(chunks), "error": None},
                client=tx,
            )

        await job.updateProgress(100)

        app_events.emit("doc:processed", {
            "documentId": document_id,
            "userId": user_id,
            "chunkCount": len(chunks),
        })

        return {"success": True, "chunks": len(chunks)}

    except Exception as error:
        is_last_attempt = job.attemptsMade >= MAX_ATTEMPTS - 1

        if is_last_attempt:
            # Change 2: mark failed AND move to the dead letter queue here,
            # instead of inside an async 'failed' event listener
            await document_repository.update(
                document_id,
                {"status": "failed", "error": str(error)},
            )
            await dead_letter_queue.add("failed-document", {
                "originalJobId": job.id,
                "originalQueue": "document-processing",
                "data": job.data,
                "error": str(error),
                "failedAt": datetime.now(timezone.utc).isoformat(),
                "attempts": job.attemptsMade + 1,
            })
            print(f"Job {job.id} permanently failed. Moved to DLQ.")

        raise  # re-raise so BullMQ records the failure and retries


def create_document_worker() -> Worker:
    # Change 3: a function that BUILDS the worker,
    # so it starts inside FastAPI's running event loop
    worker = Worker(
        "document-processing",
        process_document,
        {"connection": REDIS_URL, "concurrency": 3},
    )

    worker.on("completed", lambda job, result: print(
        f"Job {job.id} completed: {result.get('chunks')} chunks"
    ))
    worker.on("failed", lambda job, error: print(
        f"Job {job.id} failed (attempt {job.attemptsMade}): {error}"
    ))

    return worker