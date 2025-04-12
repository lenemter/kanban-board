from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    name: str = Field()


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    hashed_password: str = Field()


class UserPublic(UserBase):
    username: str


class UserCreate(UserBase):
    username: str
    password: str


class UserUpdate(UserBase):
    password: str
