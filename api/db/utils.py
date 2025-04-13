from typing import TYPE_CHECKING, Union

from sqlmodel import Session, select

if TYPE_CHECKING:
    from . import User


# "User" | None doesn't work even in python 3.13 ¯\_(ツ)_/¯
def get_user(username: str) -> Union["User", None]:
    from . import engine, User

    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()

        if user is None:
            return None

        return user
