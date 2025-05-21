from fastapi import APIRouter, HTTPException, status

import api.db
import api.dependencies
import api.schemas

router = APIRouter(tags=["boards"])


@router.get("/boards/", response_model=list[api.schemas.BoardPublic])
async def get_owned_boards(current_user: api.dependencies.CurrentUserDep):
    return api.db.get_owned_boards(current_user.id)


@router.get("/boards/shared/", response_model=list[api.schemas.BoardPublic])
async def get_shared_boards(current_user: api.dependencies.CurrentUserDep):
    return api.db.get_shared_boards(current_user.id)


@router.post("/boards/", status_code=status.HTTP_201_CREATED, response_model=api.schemas.BoardPublic)
async def create_board(current_user: api.dependencies.CurrentUserDep, board_create: api.schemas.BoardCreate):
    return api.db.create_board(owner_id=current_user.id, **board_create.model_dump())


@router.get("/boards/{board_id}", response_model=api.schemas.BoardPublic)
async def get_board(board: api.dependencies.BoardCollaboratorAccessDep):
    return board


@router.patch("/boards/{board_id}", response_model=api.schemas.BoardPublic)
async def update_board(board: api.dependencies.BoardOwnerAccessDep, board_update: api.schemas.BoardUpdate):
    return api.db.update_board(board, board_update.model_dump(exclude_unset=True))


@router.delete("/boards/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(board: api.dependencies.BoardOwnerAccessDep) -> None:
    api.db.delete_board(board)


@router.get("/boards/{board_id}/users/", response_model=list[api.schemas.UserPublic])
async def get_users(board: api.dependencies.BoardCollaboratorAccessDep):
    return api.db.get_users(board)


@router.post(
    "/boards/{board_id}/users/",
    status_code=status.HTTP_201_CREATED,
    response_model=api.schemas.BoardUserAccessPublic
)
async def add_user(board: api.dependencies.BoardOwnerAccessDep, user_id: int):
    if board.owner_id == user_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "User is the owner of this board")

    if api.db.get_user_by_id(user_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    return api.db.add_user(board, user_id)


@router.delete("/boards/{board_id}/users/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(board: api.dependencies.BoardOwnerAccessDep, user_id: int) -> None:
    if board.owner_id == user_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "Can't remove owner from the board")

    if api.db.get_user_by_id(user_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    api.db.remove_user(board, user_id)
