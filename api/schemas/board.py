from pydantic import BaseModel

from .unset_type import Unset, UnsetType


class BoardPublic(BaseModel):
    id: int
    name: str
    owner_id: int


class BoardCreate(BaseModel):
    name: str


class BoardUpdate(BaseModel):
    name: UnsetType | str = Unset
