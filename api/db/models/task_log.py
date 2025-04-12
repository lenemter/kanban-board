from datetime import datetime

from sqlmodel import Field, SQLModel


class TaskLogBase(SQLModel):
    content: str = Field()
    created_at: datetime = Field(default_factory=datetime.now)


class TaskLog(TaskLogBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")


class TaskLogPublic(TaskLogBase):
    pass
