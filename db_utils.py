import db

from sqlmodel import Session, select


def get_user(username: str) -> db.User | None:
    with Session(db.engine) as session:
        statement = select(db.User).where(db.User.username == username)
        user = session.exec(statement).first()

        return user
