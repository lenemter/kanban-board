from datetime import datetime

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    column_id: int = Field(foreign_key="column.id", ondelete="CASCADE")
    position: int = Field()
    name: str = Field()
    description: str | None = Field()
    assignee_id: int | None = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: int = Field(foreign_key="user.id")
