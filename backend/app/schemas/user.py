from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    github_id: str
    github_username: str
    created_at: datetime
