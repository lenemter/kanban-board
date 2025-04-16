from sqlmodel import Field, SQLModel

from .unset_type import Unset, UnsetType


class ColumnBase(SQLModel):
    position: int = Field()
    name: str = Field()


class Column(ColumnBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id", ondelete="CASCADE")


class ColumnPublic(ColumnBase):
    id: int


class ColumnCreate(ColumnBase):
    pass


class ColumnUpdate(SQLModel):
    position: UnsetType | int = Unset
    name: UnsetType | str = Unset
