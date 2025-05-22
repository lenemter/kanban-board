from typing import TYPE_CHECKING, Any, Union

from sqlmodel import Session, select

if TYPE_CHECKING:
    from .. import User


# "User" | None doesn't work even in python 3.13 ¯\_(ツ)_/¯
def get_user_by_id(user_id: int | None) -> Union["User", None]:
    from .. import engine, User

    with Session(engine) as session:
        return session.exec(select(User).where(User.id == user_id)).first()


# "User" | None doesn't work even in python 3.13 ¯\_(ツ)_/¯
def get_user_by_username(username: str) -> Union["User", None]:
    from .. import engine, User

    with Session(engine) as session:
        return session.exec(select(User).where(User.username == username)).first()


def register_user(**kwargs) -> "User":
    from .. import engine, User

    with Session(engine) as session:
        new_user = User(**kwargs)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return new_user


def update_user(user: "User", update: dict[str, Any]) -> "User":
    from .. import engine

    with Session(engine) as session:
        user.sqlmodel_update(update)
        session.add(user)
        session.commit()
        session.refresh(user)

        return user
