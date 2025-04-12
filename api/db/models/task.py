from sqlmodel import Field, SQLModel


class TaskBase(SQLModel):
    name: str = Field()
    description: str | None = Field()


class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    column_id: int = Field(foreign_key="column.id")


class TaskPublic(TaskBase):
    id: int


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
