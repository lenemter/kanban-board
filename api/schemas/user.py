from pydantic import BaseModel

from .unset_type import Unset, UnsetType


class UserPublic(BaseModel):
    id: int
    name: str


class UserCreate(BaseModel):
    username: str
    name: str
    password: str


class UserUpdate(BaseModel):
    name: UnsetType | str = Unset
    password: UnsetType | str = Unset
