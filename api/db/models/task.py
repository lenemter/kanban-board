from datetime import datetime

from sqlmodel import Field, SQLModel

from .unset_type import Unset, UnsetType


class TaskBase(SQLModel):
    position: int = Field()
    name: str = Field()
    description: str | None = Field()
    assignee_id: int | None = Field(foreign_key="user.id")


class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    column_id: int = Field(foreign_key="column.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: int = Field(foreign_key="user.id")


class TaskPublic(TaskBase):
    id: int
    created_at: datetime
    created_by: int


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    position: UnsetType | int = Unset
    name: UnsetType | str = Unset
    description: UnsetType | str | None = Unset
    assignee_id: UnsetType | int | None = Unset
