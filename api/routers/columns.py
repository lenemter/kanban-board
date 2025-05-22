from fastapi import APIRouter, HTTPException, status

import api.db
import api.dependencies
import api.schemas

router = APIRouter(tags=["columns"])


def validate_position(board: api.db.Board, new_position: int):
    if new_position < 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "Position must be greater or equal 0")

    for column in api.db.get_columns(board):
        if column.position == new_position:
            raise HTTPException(status.HTTP_409_CONFLICT, "This position is already taken")


@router.get("/boards/{board_id}/columns/", response_model=list[api.schemas.ColumnPublic])
async def get_columns(board: api.dependencies.BoardCollaboratorAccessDep):
    return api.db.get_columns(board)


@router.post(
    "/boards/{board_id}/columns/",
    status_code=status.HTTP_201_CREATED,
    response_model=api.schemas.ColumnPublic
)
async def create_column(board: api.dependencies.BoardCollaboratorAccessDep, column_create: api.schemas.ColumnCreate):
    validate_position(board, column_create.position)

    return api.db.create_column(board_id=board.id, **column_create.model_dump())


@router.get("/columns/{column_id}", response_model=api.schemas.ColumnPublic)
async def get_column(
    board_and_column: api.dependencies.BoardColumnDep,
):
    _, column = board_and_column
    return column


@router.patch("/columns/{column_id}", response_model=api.schemas.ColumnPublic)
async def update_column(board_and_column: api.dependencies.BoardColumnDep, column_update: api.schemas.ColumnUpdate):
    board, column = board_and_column

    if not isinstance(column_update.position, api.schemas.UnsetType) and column_update.position != column.position:
        validate_position(board, column_update.position)

    return api.db.update_column(column, column_update.model_dump(exclude_unset=True))


@router.delete("/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(board_and_column: api.dependencies.BoardColumnDep) -> None:
    _, column = board_and_column
    api.db.delete_column(column)
