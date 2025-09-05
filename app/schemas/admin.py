from pydantic import BaseModel
from uuid import UUID


class AdminOut(BaseModel):
    user_id: UUID

    class Config:
        from_attributes = True
 
