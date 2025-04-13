from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select

import api.db
import api.dependencies

router = APIRouter(tags=["columns"])


def validate_arguments(board: api.db.Board, new_position: int, session: Session):
    if new_position < 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "Position must be greater or equal 0")

    columns = session.exec(
        select(api.db.Column)
        .where(api.db.Column.board_id == board.id)
    ).all()

    for column in columns:
        if column.position == new_position:
            raise HTTPException(status.HTTP_409_CONFLICT, "This position is already taken")


@router.get("/boards/{board_id}/columns/", response_model=list[api.db.ColumnPublic])
async def get_columns(
    board: api.dependencies.BoardUserDep,
    session: api.dependencies.SessionDep,
):
    return list(
        session.exec(
            select(api.db.Column).where(
                api.db.Column.board_id == board.id
            )
        ).all()
    )


@router.post("/boards/{board_id}/columns/", status_code=status.HTTP_201_CREATED, response_model=api.db.ColumnPublic)
async def create_column(
    board: api.dependencies.BoardUserDep,
    column_create: api.db.ColumnCreate,
    session: api.dependencies.SessionDep,
):
    validate_arguments(board, column_create.position, session)

    column = api.db.Column(board_id=board.id, **column_create.model_dump())
    session.add(column)
    session.commit()
    session.refresh(column)

    return column


@router.get("/columns/{column_id}", response_model=api.db.ColumnPublic)
async def get_column(
    column: api.dependencies.ColumnDep,
):
    return column


@router.patch("/columns/{column_id}", response_model=api.db.ColumnPublic)
async def update_column(
    column: api.dependencies.ColumnDep,
    column_update: api.db.ColumnUpdate,
    session: api.dependencies.SessionDep,
):
    board = session.get(api.db.Board, column.board_id)
    if board is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error")

    if column_update.position is not None:
        validate_arguments(board, column_update.position, session)

    column.sqlmodel_update(column_update.model_dump(exclude_unset=True))
    session.add(column)
    session.commit()
    session.refresh(column)

    return column


@router.delete("/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(
    column: api.dependencies.ColumnDep,
    session: api.dependencies.SessionDep,
) -> None:
    session.delete(column)
    session.commit()
