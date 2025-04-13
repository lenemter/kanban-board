from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlmodel import Session, select

import api.db

# --- Session ---


def get_session():
    with Session(api.db.engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

# --- User Validation ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> api.db.UserFromDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, api.utils.read_secret("SECRET_KEY"), algorithms=[api.utils.HASH_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = api.db.get_user(username=username)
    if user is None:
        raise credentials_exception
    if user.id is None:
        raise credentials_exception

    return api.db.UserFromDB(**user.model_dump())


CurrentUserDep = Annotated[api.db.UserFromDB, Depends(get_current_user)]

# -- Board ---


def owner_get_board(board_id: int, current_user: CurrentUserDep, session: SessionDep) -> api.db.Board:
    board = session.get(api.db.Board, board_id)
    if board is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Board not found")
    if board.owner_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not enough permissions")

    return board


def check_user_access(user: api.db.UserFromDB, board: api.db.Board) -> bool:
    if board.owner_id == user.id:
        return True

    with Session(api.db.engine) as session:
        board_user_access = session.exec(
            select(api.db.BoardUserAccess).where(
                api.db.BoardUserAccess.board_id == board.id,
                api.db.BoardUserAccess.user_id == user.id
            )
        ).first()

        return board_user_access is not None


def user_get_board(board_id: int, current_user: CurrentUserDep, session: SessionDep) -> api.db.Board:
    board = session.get(api.db.Board, board_id)
    if board is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Board not found")
    if not check_user_access(current_user, board):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not enough permissions")

    return board


BoardOwnerDep = Annotated[api.db.Board, Depends(owner_get_board)]
BoardUserDep = Annotated[api.db.Board, Depends(user_get_board)]

# --- Column ---


def get_column(current_user: CurrentUserDep, column_id: int, session: SessionDep) -> api.db.Column:
    column = session.get(api.db.Column, column_id)
    if column is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Column not found")

    user_get_board(column.board_id, current_user, session)

    return column


ColumnDep = Annotated[api.db.Column, Depends(get_column)]

# --- Task ---


def get_task(current_user: CurrentUserDep, task_id: int, session: SessionDep) -> api.db.Task:
    task = session.get(api.db.Task, task_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")

    get_column(current_user, task.column_id, session)

    return task


TaskDep = Annotated[api.db.Task, Depends(get_task)]
