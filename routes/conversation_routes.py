from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from middlewares.authorize_middleware import require_permission
from services import conversation_service

router = APIRouter()


class SendMessageBody(BaseModel):
    content: str = Field(min_length=1, max_length=10000)
    documentId: str | None = None


@router.get("/")
async def list_conversation(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: dict = Depends(require_permission("conversations:read")),
):
    return await conversation_service.list_conversations(user["id"], page, limit)

@router.post("/{conversation_id}/messages", status_code=201)
async def send_message_route(
    conversation_id: str,
    body: SendMessageBody,
    user: dict = Depends(require_permission("conversations:create")),
):
    result = await conversation_service.send_message(
        conversation_id, user["id"], body.content, body.documentId
    )
    return {"success": True, "data": result}