from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    hashed_password: str = Field()
    name: str = Field()


class Board(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    name: str = Field()


class BoardUserAccess(SQLModel, table=True):
    board_id: int = Field(foreign_key="board.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)


class Column(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id")
    position: int = Field()
    name: str = Field()


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    column_id: int = Field(foreign_key="column.id")
    name: str = Field()
    description: str | None = Field()


class TaskLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    content: str = Field()
    created_at: datetime = Field(default_factory=datetime.now)
