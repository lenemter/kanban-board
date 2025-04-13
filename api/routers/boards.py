from typing import Any
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

import api.db
import api.dependencies

router = APIRouter(tags=["boards"])


@router.get("/boards/", response_model=list[api.db.BoardPublic])
async def get_boards(
    current_user: api.dependencies.CurrentUserDep,
    session: api.dependencies.SessionDep
):
    return list(
        session.exec(
            select(api.db.Board).where(
                api.db.Board.owner_id == current_user.id
            )
        ).all()
    )


@router.get("/boards/shared/", response_model=list[api.db.BoardPublic])
async def get_shared_boards(
    current_user: api.dependencies.CurrentUserDep,
    session: api.dependencies.SessionDep
):
    owned = list(
        session.exec(
            select(api.db.Board).where(
                api.db.Board.owner_id == current_user.id
            )
        ).all()
    )

    shared = list(
        session.exec(
            select(api.db.Board)
            .join(api.db.BoardUserAccess)
            .where(api.db.BoardUserAccess.user_id == current_user.id)
        ).all()
    )

    return owned + shared


@router.post("/boards/", status_code=status.HTTP_201_CREATED, response_model=api.db.BoardPublic)
async def create_board(
    current_user: api.dependencies.CurrentUserDep,
    board_create: api.db.BoardCreate,
    session: api.dependencies.SessionDep,
):
    new_board = api.db.Board(owner_id=current_user.id, **board_create.model_dump())
    session.add(new_board)
    session.commit()
    session.refresh(new_board)

    return new_board


@router.get("/boards/{board_id}", response_model=api.db.BoardPublic)
async def get_board(
    board: api.dependencies.BoardUserDep,
):
    return board


@router.patch("/boards/{board_id}", response_model=api.db.BoardPublic)
async def update_board(
    board: api.dependencies.BoardOwnerDep,
    board_update: api.db.BoardUpdate,
    session: api.dependencies.SessionDep,
):
    board.sqlmodel_update(board_update.model_dump(exclude_unset=True))
    session.add(board)
    session.commit()
    session.refresh(board)

    return board


@router.delete("/boards/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board: api.dependencies.BoardOwnerDep,
    session: api.dependencies.SessionDep,
) -> None:
    session.delete(board)
    session.commit()


@router.post("/boards/{board_id}/add_user/", status_code=status.HTTP_201_CREATED)
async def add_user(
    board: api.dependencies.BoardOwnerDep,
    user_id: str,
    session: api.dependencies.SessionDep,
) -> api.db.BoardUserAccess:
    user = session.get(api.db.User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    conflict_exception = HTTPException(status.HTTP_409_CONFLICT, "User already has access to this board")

    if board.owner_id == user_id:
        raise conflict_exception

    old_board_user_access = session.exec(
        select(api.db.BoardUserAccess).where(
            api.db.BoardUserAccess.board_id == board.id,
            api.db.BoardUserAccess.user_id == user_id
        )
    ).first()

    if old_board_user_access is not None:
        raise conflict_exception

    board_user_access = api.db.BoardUserAccess(board_id=board.id, user_id=user.id)
    session.add(board_user_access)
    session.commit()
    session.refresh(board_user_access)

    return board_user_access


@router.get("/boards/{board_id}/users/", response_model=list[api.db.UserPublic])
async def get_users(
    board: api.dependencies.BoardUserDep,
    current_user: api.dependencies.CurrentUserDep,
    session: api.dependencies.SessionDep,
):
    board_user_accesses = session.exec(
        select(api.db.BoardUserAccess).where(
            api.db.BoardUserAccess.board_id == board.id
        )
    ).all()

    result: list[Any] = [current_user]
    for board_user_access in board_user_accesses:
        result.append(session.get(api.db.User, board_user_access.user_id))

    return result
