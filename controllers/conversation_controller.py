from services import conversation_service
from validators.conversation_validator import SendMessageBody


async def list_conversations(page: int, limit: int, user: dict) -> dict:
    return await conversation_service.list_conversations(user["id"], page, limit)


async def send_message(
    conversation_id: str, body: SendMessageBody, user: dict
) -> dict:
    result = await conversation_service.send_message(
        conversation_id, user["id"], body.content, body.documentId
    )
    return {"success": True, "data": result}
