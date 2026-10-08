from fastapi import APIRouter, Depends, Query

from controllers import conversation_controller
from middlewares.authorize_middleware import require_permission
from validators.conversation_validator import SendMessageBody

router = APIRouter()


@router.get("/")
async def list_conversations(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: dict = Depends(require_permission("conversations:read")),
):
    return await conversation_controller.list_conversations(page, limit, user)


@router.post("/{conversation_id}/messages", status_code=201)
async def send_message(
    conversation_id: str,
    body: SendMessageBody,
    user: dict = Depends(require_permission("conversations:create")),
):
    return await conversation_controller.send_message(conversation_id, body, user)
