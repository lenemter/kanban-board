from typing import Any
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

import api.db
import api.dependencies
import api.schemas

router = APIRouter(tags=["boards"])


@router.get("/boards/", response_model=list[api.schemas.BoardPublic])
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


@router.get("/boards/shared/", response_model=list[api.schemas.BoardPublic])
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


@router.post("/boards/", status_code=status.HTTP_201_CREATED, response_model=api.schemas.BoardPublic)
async def create_board(
    current_user: api.dependencies.CurrentUserDep,
    board_create: api.schemas.BoardCreate,
    session: api.dependencies.SessionDep,
):
    new_board = api.db.Board(owner_id=current_user.id, **board_create.model_dump())
    session.add(new_board)
    session.commit()
    session.refresh(new_board)

    return new_board


@router.get("/boards/{board_id}", response_model=api.schemas.BoardPublic)
async def get_board(
    board: api.dependencies.BoardCollaboratorAccessDep,
):
    return board


@router.patch("/boards/{board_id}", response_model=api.schemas.BoardPublic)
async def update_board(
    board: api.dependencies.BoardOwnerAccessDep,
    board_update: api.schemas.BoardUpdate,
    session: api.dependencies.SessionDep,
):
    board.sqlmodel_update(board_update.model_dump(exclude_unset=True))
    session.add(board)
    session.commit()
    session.refresh(board)

    return board


@router.delete("/boards/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board: api.dependencies.BoardOwnerAccessDep,
    session: api.dependencies.SessionDep,
) -> None:
    session.delete(board)
    session.commit()


@router.get("/boards/{board_id}/users/", response_model=list[api.schemas.UserPublic])
async def get_users(
    board: api.dependencies.BoardCollaboratorAccessDep,
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


@router.post(
    "/boards/{board_id}/users/",
    status_code=status.HTTP_201_CREATED,
    response_model=api.schemas.BoardUserAccessPublic
)
async def add_user(
    board: api.dependencies.BoardOwnerAccessDep,
    user_id: int,
    session: api.dependencies.SessionDep,
):
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


@router.delete("/boards/{board_id}/users/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(
    board: api.dependencies.BoardOwnerAccessDep,
    user_id: int,
    session: api.dependencies.SessionDep,
) -> None:
    user = session.get(api.db.User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    if board.owner_id == user_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "Can't remove owner from the board")

    board_user_access = session.exec(
        select(api.db.BoardUserAccess).where(
            api.db.BoardUserAccess.board_id == board.id,
            api.db.BoardUserAccess.user_id == user_id
        )
    ).first()

    if board_user_access is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "This user doesn't have access to the board")

    session.delete(board_user_access)
    session.commit()
