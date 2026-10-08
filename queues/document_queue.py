import time

from bullmq import Queue

from queues.connection_queue import REDIS_URL

MAX_ATTEMPTS = 3

document_queue = Queue("document-processing", {"connection": REDIS_URL})

JOB_OPTIONS = {
    "attempts": MAX_ATTEMPTS,
    "backoff": {"type": "exponential", "delay": 2000},  # milliseconds
    "removeOnComplete": {"count": 200},
    "removeOnFail": {"count": 500},
}


async def queue_document_for_processing(document_id: str, user_id: str) -> str:
    job = await document_queue.add(
        "process-document",
        {
            "documentId": document_id,
            "userId": user_id,
            "queuedAt": int(time.time() * 1000),
        },
        JOB_OPTIONS,
    )
    return job.id