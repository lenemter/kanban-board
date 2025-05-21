from sqlmodel import Field, SQLModel


class Board(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    name: str = Field()
