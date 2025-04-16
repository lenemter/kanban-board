from sqlmodel import Field, SQLModel

from .unset_type import Unset, UnsetType


class UserBase(SQLModel):
    name: str = Field()


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    hashed_password: str = Field()


class UserPublic(UserBase):
    id: int


class UserCreate(UserBase):
    username: str
    password: str


class UserUpdate(SQLModel):
    name: UnsetType | str = Unset
    password: UnsetType | str = Unset
