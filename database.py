from sqlmodel import Field, Session, SQLModel, create_engine, select


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field()


class Board(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field()
    name: str = Field()

class BoardUserAccess(SQLModel, table=True):
    board_id: int = Field()
    user_id: int = Field()
