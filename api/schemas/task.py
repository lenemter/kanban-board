from datetime import datetime

from pydantic import BaseModel

from .unset_type import Unset, UnsetType


class TaskPublic(BaseModel):
    id: int
    position: int
    name: str
    description: str | None
    assignee_id: int | None
    created_at: datetime
    created_by: int


class TaskCreate(BaseModel):
    name: str
    description: str | None
    assignee_id: int | None


class TaskUpdate(BaseModel):
    column_id: UnsetType | int = Unset
    position: UnsetType | int = Unset
    name: UnsetType | str = Unset
    description: UnsetType | str | None = Unset
    assignee_id: UnsetType | int | None = Unset


class TaskFilter(BaseModel):
    assignee_id: UnsetType | int | str | None = Unset
    created_by: UnsetType | int = Unset
