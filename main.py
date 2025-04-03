from datetime import timedelta
from typing import Annotated

import auth
import db
import db_utils
import utils

import dotenv
from fastapi import Depends, FastAPI, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
import pydantic

ACCESS_TOKEN_EXPIRE_MINUTES = 30

dotenv.load_dotenv()

db.create_db_and_tables()

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/my-token")
async def boards(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> auth.Token:
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    name: Annotated[str, Form()]
) -> auth.Token:
    user = auth.register_user(username, password, name)
    if not user:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")

    return auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> db.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, utils.read_secret("SECRET_KEY"), algorithms=(utils.HASH_ALGORITHM,))
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = db_utils.get_user(username=username)
    if not user:
        raise credentials_exception

    return user


@app.get("/user")
async def read_users_me(current_user: Annotated[db.User, Depends(get_current_user)]) -> db.User:
    return current_user
