from sqlmodel import Field, SQLModel


class ColumnBase(SQLModel):
    position: int = Field()
    name: str = Field()


class Column(ColumnBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id")


class ColumnPublic(ColumnBase):
    id: int


class ColumnCreate(ColumnBase):
    pass


class ColumnUpdate(ColumnBase):
    pass
