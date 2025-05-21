from datetime import datetime

from sqlmodel import Field, SQLModel


class TaskLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id", ondelete="CASCADE")
    content: str = Field()
    created_at: datetime = Field(default_factory=datetime.now)
