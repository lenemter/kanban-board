from pydantic import BaseModel

from .unset_type import Unset, UnsetType


class ColumnPublic(BaseModel):
    id: int
    position: int
    name: str


class ColumnCreate(BaseModel):
    position: int
    name: str


class ColumnUpdate(BaseModel):
    position: UnsetType | int = Unset
    name: UnsetType | str = Unset
