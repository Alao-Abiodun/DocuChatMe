import json
from datetime import datetime, timezone

from lib.events_lib import app_events
from repositories import usage_log_repository

DOC_EVENTS = {
    "CREATED": "doc:created",
    "PROCESSED": "doc:processed",
    "DELETED": "doc:deleted",
}


@app_events.on(DOC_EVENTS["CREATED"])
async def log_document_created(data: dict):
    try:
        await usage_log_repository.create(
            data["userId"],
            action="document_created",
            metadata=json.dumps({
                "documentId": data["documentId"],
                "title": data["title"],
                "fileSizeBytes": data["fileSizeBytes"],
            }),
        )
    except Exception as error:
        print(f"Failed to log document creation: {error}")


@app_events.on(DOC_EVENTS["DELETED"])
async def log_document_deleted(data: dict):
    try:
        await usage_log_repository.create(
            data["deletedBy"],
            action="document_deleted",
            metadata=json.dumps({
                "documentId": data["documentId"],
                "title": data["title"],
                "deletedAt": datetime.now(timezone.utc).isoformat(),
            }),
        )
    except Exception as error:
        print(f"Failed to log document deletion: {error}")
