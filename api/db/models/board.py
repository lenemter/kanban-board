from sqlmodel import Field, SQLModel


class BoardBase(SQLModel):
    name: str = Field()


class Board(BoardBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")


class BoardPublic(BoardBase):
    id: int
    owner_id: int


class BoardCreate(BoardBase):
    pass


class BoardUpdate(SQLModel):
    name: str | None = None
