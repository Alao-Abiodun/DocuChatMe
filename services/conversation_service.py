import asyncio
from datetime import datetime, timezone

from lib.errors_lib import NotFoundError
from lib.transaction_lib import transaction
from repositories import (
    conversation_repository,
    document_repository,
    message_repository,
    usage_log_repository,
)


async def list_conversations(user_id: str, page: int, limit: int) -> dict:
    conversations, total = await asyncio.gather(
        conversation_repository.list_with_latest_message(
            user_id, skip=(page - 1) * limit, take=limit
        ),
        conversation_repository.count(user_id),
    )

    # One grouped query for the message counts of every conversation on this page
    counts: dict[str, int] = {}
    ids = [c.id for c in conversations]
    if ids:
        rows = await message_repository.count_by_conversation_ids(ids)
        counts = {row["conversationId"]: row["_count"]["_all"] for row in rows}

    return {
        "data": [
            {
                "id": c.id,
                "title": c.title,
                "messageCount": counts.get(c.id, 0),
                "lastMessage": (
                    {
                        "content": c.messages[0].content,
                        "role": c.messages[0].role,
                        "createdAt": c.messages[0].createdAt,
                    }
                    if c.messages
                    else None
                ),
                "updatedAt": c.updatedAt,
            }
            for c in conversations
        ],
        "meta": {"page": page, "limit": limit, "total": total},
    }


async def send_message(
    conversation_id: str,
    user_id: str,
    content: str,
    document_id: str | None = None,
) -> dict:
    # Read-only validation OUTSIDE the transaction, so the tx stays short
    if document_id:
        doc = await document_repository.find_active_owned(document_id, user_id)
        if not doc:
            raise NotFoundError("Document not found")

    doc_fields = {"documentId": document_id} if document_id else {}

    # Commits on clean exit, rolls back automatically if anything raises
    async with transaction() as tx:
        conversation = await conversation_repository.find_owned(
            conversation_id, user_id, client=tx
        )
        if not conversation:
            raise NotFoundError("Conversation not found")

        user_message = await message_repository.create(
            {
                "conversationId": conversation_id,
                "role": "user",
                "content": content,
                **doc_fields,
            },
            client=tx,
        )

        await conversation_repository.touch(
            conversation_id, datetime.now(timezone.utc), client=tx
        )

        # Placeholder assistant message (RAG pipeline arrives in Week 4)
        assistant_message = await message_repository.create(
            {
                "conversationId": conversation_id,
                "role": "assistant",
                "content": "AI response placeholder (Week 4)",
                "promptTokens": 0,
                "completionTokens": 0,
                "costUsd": 0,
                **doc_fields,
            },
            client=tx,
        )

        await usage_log_repository.create(
            user_id, action="chat", tokens=0, cost_usd=0, client=tx
        )

    return {"userMessage": user_message, "assistantMessage": assistant_message}
