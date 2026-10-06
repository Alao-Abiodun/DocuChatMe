import asyncio
from lib.prisma_lib import prisma
from lib.errors_lib import NotFoundError
from datetime import datetime, timezone


async def list_conversations(user_id: str, page: int, limit: int) -> dict:
    # Queries 1 and 2 run in parallel
    conversations, total = await asyncio.gather(
        prisma.conversation.find_many(
            where={"userId": user_id},
            order={"updatedAt": "desc"},
            skip=(page - 1) * limit,
            take=limit,
            include={
                "messages": {
                    "order_by": {"createdAt": "desc"},
                    "take": 1,  # only the latest message
                }
            },
        ),
        prisma.conversation.count(where={"userId": user_id}),
    )

    # Query 3: message counts for ALL conversations on this page at once
    counts: dict[str, int] = {}
    ids = [c.id for c in conversations]
    if ids:
        rows = await prisma.message.group_by(
            by=["conversationId"],
            count=True,
            where={"conversationId": {"in": ids}},
        )
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
        doc = await prisma.document.find_first(
            where={"id": document_id, "userId": user_id, "deletedAt": None}
        )
        if not doc:
            raise NotFoundError("Document not found")

    doc_fields = {"documentId": document_id} if document_id else {}

    # Commits on clean exit, rolls back automatically if anything raises
    async with prisma.tx() as tx:
        # 1. Verify the conversation belongs to this user
        conversation = await tx.conversation.find_first(
            where={"id": conversation_id, "userId": user_id}
        )
        if not conversation:
            raise NotFoundError("Conversation not found")

        # 2. User's message
        user_message = await tx.message.create(
            data={
                "conversationId": conversation_id,
                "role": "user",
                "content": content,
                **doc_fields,
            }
        )

        # 3. Touch updatedAt (no other field changes, so set it explicitly)
        await tx.conversation.update(
            where={"id": conversation_id},
            data={"updatedAt": datetime.now(timezone.utc)},
        )

        # 4. Placeholder assistant message (RAG pipeline arrives in Week 4)
        assistant_message = await tx.message.create(
            data={
                "conversationId": conversation_id,
                "role": "assistant",
                "content": "AI response placeholder (Week 4)",
                "promptTokens": 0,
                "completionTokens": 0,
                "costUsd": 0,
                **doc_fields,
            }
        )

        # 5. Usage log
        await tx.usagelog.create(
            data={"userId": user_id, "action": "chat", "tokens": 0, "costUsd": 0}
        )

    return {"userMessage": user_message, "assistantMessage": assistant_message}