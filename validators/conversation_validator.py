from pydantic import BaseModel, Field


class SendMessageBody(BaseModel):
    content: str = Field(min_length=1, max_length=10000)
    documentId: str | None = None
