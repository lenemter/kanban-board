from sqlmodel import Field, SQLModel


class Column(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id", ondelete="CASCADE")
    position: int = Field()
    name: str = Field()
