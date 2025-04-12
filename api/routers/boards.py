from typing import Any
from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select

import api.db
import api.dependencies

router = APIRouter(tags=["boards"])


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


@router.get("/boards/", response_model=list[api.db.BoardPublic])
async def get_boards(current_user: api.dependencies.CurrentUserDep):
    return api.db.get_boards(current_user.id)


@router.get("/boards/{board_id}", response_model=api.db.BoardPublic)
async def get_board(
    board_id: int,
    current_user: api.dependencies.CurrentUserDep,
    session: api.dependencies.SessionDep,
):
    board = session.get(api.db.Board, board_id)
    if board is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Board not found")
    if not check_user_access(current_user, board):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not enough permissions")

    return board


@router.post("/boards/new/", status_code=status.HTTP_201_CREATED, response_model=api.db.BoardPublic)
async def create_board(
    current_user: api.dependencies.CurrentUserDep,
    session: api.dependencies.SessionDep,
    board_create: api.db.BoardCreate
):
    new_board = api.db.Board(owner_id=current_user.id, name=board_create.name)
    session.add(new_board)
    session.commit()
    session.refresh(new_board)

    return new_board


@router.patch("/boards/{board_id}", response_model=api.db.BoardPublic)
async def update_board(
    board_id: int,
    board_update: api.db.BoardUpdate,
    current_user: api.dependencies.CurrentUserDep,
    session: api.dependencies.SessionDep,
):
    board = session.get(api.db.Board, board_id)
    if board is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Board not found")
    if board.owner_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not enough permissions")

    board.sqlmodel_update(board_update.model_dump(exclude_unset=True))
    session.add(board)
    session.commit()
    session.refresh(board)

    return board


@router.delete("/boards/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: int,
    current_user: api.dependencies.CurrentUserDep,
    session: api.dependencies.SessionDep,
) -> None:
    board = session.get(api.db.Board, board_id)
    if board is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Board not found")
    if board.owner_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not enough permissions")

    session.delete(board)
    session.commit()


@router.post("/boards/{board_id}/add_user/", status_code=status.HTTP_201_CREATED)
async def add_user(
    board_id: int,
    user_id: str,
    current_user: api.dependencies.CurrentUserDep,
    session: api.dependencies.SessionDep,
) -> api.db.BoardUserAccess:
    board = session.get(api.db.Board, board_id)
    if board is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Board not found")
    if board.owner_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not enough permissions")

    user = session.get(api.db.User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    old_board_user_access = session.exec(
        select(api.db.BoardUserAccess).where(
            api.db.BoardUserAccess.board_id == board.id,
            api.db.BoardUserAccess.user_id == user_id
        )
    ).first()

    if old_board_user_access is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "User already has access to this board")

    board_user_access = api.db.BoardUserAccess(board_id=board_id, user_id=user.id)
    session.add(board_user_access)
    session.commit()
    session.refresh(board_user_access)

    return board_user_access


@router.get("/boards/{board_id}/users/", response_model=list[api.db.UserPublic])
async def get_users(
    board_id: int,
    current_user: api.dependencies.CurrentUserDep,
    session: api.dependencies.SessionDep,
):
    board = session.get(api.db.Board, board_id)
    if board is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Board not found")
    if not check_user_access(current_user, board):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not enough permissions")

    board_user_accesses = session.exec(
        select(api.db.BoardUserAccess).where(
            api.db.BoardUserAccess.board_id == board.id
        )
    ).all()

    result: list[Any] = [current_user]
    for board_user_access in board_user_accesses:
        result.append(session.get(api.db.User, board_user_access.user_id))

    return result
