from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import jwt
import bcrypt
import pydantic
from sqlmodel import Session

import api.db
import api.utils

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(tags=["auth"])


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def authenticate_user(username: str, password: str) -> api.db.User | None:
    user = api.db.get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user


def register_user(username: str, password: str, name: str) -> api.db.User | None:
    if (api.db.get_user(username=username) is not None):
        return None

    new_user = api.db.User(username=username, hashed_password=get_password_hash(password), name=name)

    with Session(api.db.engine) as session:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

    return new_user


def create_access_token(data: dict, expires_delta: timedelta) -> Token:
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode = data.copy()
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, api.utils.read_secret("SECRET_KEY"), algorithm=api.utils.HASH_ALGORITHM)

    return Token(access_token=encoded_jwt, token_type="bearer")


@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    name: Annotated[str, Form()],
) -> Token:
    user = register_user(username, password, name)
    if not user:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")

    return create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
