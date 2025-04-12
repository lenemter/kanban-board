from sqlmodel import Field, SQLModel


class BoardUserAccess(SQLModel, table=True):
    board_id: int = Field(foreign_key="board.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)
