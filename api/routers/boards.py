from fastapi import APIRouter, HTTPException, status

import api.db
import api.dependencies

router = APIRouter(tags=["boards"])


@router.get("/boards/", response_model=list[api.db.BoardPublic])
async def get_boards(
    current_user: api.dependencies.CurrentUserDep,
):
    if current_user.id is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error")

    user_id: int = current_user.id

    return api.db.get_boards(user_id)


@router.get("/boards/{board_id}", response_model=api.db.BoardPublic)
async def get_board(
    board_id: int,
    current_user: api.dependencies.CurrentUserDep,
    session: api.dependencies.SessionDep
):
    if current_user.id is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error")

    user_id: int = current_user.id

    board = session.get(api.db.Board, board_id)
    if board is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Board not found")
    if board.owner_id != user_id:
        # TODO: handle BoardUserAccess
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not enough permissions")

    return board


@router.post("/boards/new/", status_code=status.HTTP_201_CREATED, response_model=api.db.BoardPublic)
async def create_board(
    current_user: api.dependencies.CurrentUserDep,
    session: api.dependencies.SessionDep,
    board_create: api.db.BoardCreate
):
    if current_user.id is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error")

    new_board = api.db.Board(owner_id=current_user.id, name=board_create.name)
    session.add(new_board)
    session.commit()
    session.refresh(new_board)

    return new_board
