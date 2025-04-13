from fastapi import APIRouter, status
from sqlmodel import select

import api.db
import api.dependencies

router = APIRouter(tags=["columns"])


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
    # TODO: validate position

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


@router.get("/columns/{column_id}/tasks/", response_model=api.db.TaskPublic)
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


@router.post("/columns/{column_id}/tasks/", status_code=status.HTTP_201_CREATED, response_model=api.db.TaskPublic)
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


@router.get("/columns/{column_id}/tasks/{task_id}", response_model=api.db.TaskPublic)
async def get_task(
    task: api.dependencies.TaskDep,
):
    return task


@router.patch("/columns/{column_id}/tasks/{task_id}", response_model=api.db.TaskPublic)
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


@router.delete("/columns/{column_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task: api.dependencies.TaskDep,
    session: api.dependencies.SessionDep,
):
    session.delete(task)
    session.commit()
