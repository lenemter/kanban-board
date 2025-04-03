from datetime import datetime, timedelta, timezone

import db
import db_utils
import utils

import jwt
import bcrypt
import pydantic
from sqlmodel import Session


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def authenticate_user(username: str, password: str) -> db.User | None:
    user = db_utils.get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user


def register_user(username: str, password: str, name: str) -> db.User | None:
    if (db_utils.get_user(username=username) is not None):
        return None

    new_user = db.User(username=username, hashed_password=get_password_hash(password), name=name)

    with Session(db.engine) as session:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

    return new_user


def create_access_token(data: dict, expires_delta: timedelta) -> Token:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, utils.read_secret("SECRET_KEY"), algorithm=utils.HASH_ALGORITHM)

    return Token(access_token=encoded_jwt, token_type="bearer")
