from datetime import datetime

from pydantic import BaseModel


class TaskLogPublic(BaseModel):
    content: str
    created_at: datetime
