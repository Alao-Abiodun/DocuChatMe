from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class ListDocumentsQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    status: Literal["pending", "processing", "ready", "failed"] | None = None
    search: str | None = Field(None, max_length=200)
    sort_by: Literal["createdAt", "title", "chunkCount"] = Field("createdAt", alias="sortBy")
    sort_order: Literal["asc", "desc"] = Field("desc", alias="sortOrder")
    