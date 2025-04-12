from typing import TYPE_CHECKING, Union

from sqlmodel import Session, select

if TYPE_CHECKING:
    from . import UserFromDB, Board


# "UserFromDB" | None doesn't work even in python 3.13 ¯\_(ツ)_/¯
def get_user(username: str) -> Union["UserFromDB", None]:
    from . import engine, User, UserFromDB

    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()

        if user is None:
            return None

        return UserFromDB(**user.model_dump())


def get_boards(owner_id: int) -> list["Board"]:
    from . import engine, Board

    with Session(engine) as session:
        statement = select(Board).where(Board.owner_id == owner_id)
        boards = session.exec(statement).all()

        return list(boards)
