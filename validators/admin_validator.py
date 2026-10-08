from pydantic import BaseModel, Field


class AssignRoleBody(BaseModel):
    roleName: str = Field(min_length=1)
