from typing import Any
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

import api.db
import api.dependencies

router = APIRouter(tags=["boards"])


@router.get("/boards/", response_model=list[api.db.BoardPublic])
async def get_boards(current_user: api.dependencies.CurrentUserDep):
    return api.db.get_boards(current_user.id)


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

    old_board_user_access = session.exec(
        select(api.db.BoardUserAccess).where(
            api.db.BoardUserAccess.board_id == board.id,
            api.db.BoardUserAccess.user_id == user_id
        )
    ).first()

    if old_board_user_access is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "User already has access to this board")

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
    # TODO: validate position

    column = api.db.Column(board_id=board.id, **column_create.model_dump())
    session.add(column)
    session.commit()
    session.refresh(column)

    return column


@router.get("/boards/{board_id}/columns/{column_id}", response_model=api.db.ColumnPublic)
async def get_column(
    column: api.dependencies.ColumnDep,
):
    return column


@router.patch("/boards/{board_id}/columns/{column_id}", response_model=api.db.ColumnPublic)
async def update_column(
    column: api.dependencies.ColumnDep,
    column_update: api.db.ColumnUpdate,
    session: api.dependencies.SessionDep,
):
    # TODO: validate position

    column.sqlmodel_update(column_update.model_dump(exclude_unset=True))
    session.add(column)
    session.commit()
    session.refresh(column)

    return column


@router.delete("/boards/{board_id}/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(
    column: api.dependencies.ColumnDep,
    session: api.dependencies.SessionDep,
) -> None:
    session.delete(column)
    session.commit()


@router.get("/boards/{board_id}/columns/{column_id}/tasks/", response_model=api.db.TaskPublic)
async def get_tasks(
    column: api.dependencies.ColumnDep,
    session: api.dependencies.SessionDep,
):
    return list(
        session.exec(
            select(api.db.Task).where(
                api.db.Task.column_id == column.id
            )
        ).all()
    )


@router.post(
    "/boards/{board_id}/columns/{column_id}/tasks/",
    status_code=status.HTTP_201_CREATED,
    response_model=api.db.TaskPublic,
)
async def add_task(
    column: api.dependencies.ColumnDep,
    task_create: api.db.TaskCreate,
    session: api.dependencies.SessionDep,
):
    task = api.db.Task(column_id=column.id, **task_create.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get("/boards/{board_id}/columns/{column_id}/tasks/{task_id}", response_model=api.db.TaskPublic)
async def get_task(
    task: api.dependencies.TaskDep,
):
    return task


@router.patch("/boards/{board_id}/columns/{column_id}/tasks/{task_id}", response_model=api.db.TaskPublic)
async def update_task(
    task: api.dependencies.TaskDep,
    task_update: api.db.TaskUpdate,
    session: api.dependencies.SessionDep,
):
    task.sqlmodel_update(task_update.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete("/boards/{board_id}/columns/{column_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task: api.dependencies.TaskDep,
    session: api.dependencies.SessionDep,
):
    session.delete(task)
    session.commit()
