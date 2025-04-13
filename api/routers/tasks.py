from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select

import api.db
import api.dependencies

router = APIRouter(tags=["tasks"])


def validate_new_position(column: api.db.Column, new_position: int, session: Session):
    if new_position < 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "Position must be greater or equal 0")

    tasks = session.exec(
        select(api.db.Task)
        .where(api.db.Task.column_id == column.id)
    ).all()

    for task in tasks:
        if task.position == new_position:
            raise HTTPException(status.HTTP_409_CONFLICT, "This position is already taken")


def validate_new_assignee(column: api.db.Column, assignee_id: int, session: Session):
    assigned_user = session.get(api.db.User, assignee_id)
    if assigned_user is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "This user doesn't exist")

    board = session.get(api.db.Board, column.board_id)
    if board is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error")

    if not api.dependencies.check_user_access(api.db.UserFromDB(**assigned_user.model_dump()), board):
        raise HTTPException(status.HTTP_409_CONFLICT, "This user doesn't have access to this board")


@router.get("/columns/{column_id}/tasks/", response_model=list[api.db.TaskPublic])
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
    current_user: api.dependencies.CurrentUserDep,
    session: api.dependencies.SessionDep,
):
    validate_new_position(column, task_create.position, session)
    if task_create.assignee_id is not None:
        validate_new_assignee(column, task_create.assignee_id, session)

    task = api.db.Task(column_id=column.id, created_by=current_user.id, **task_create.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get("/tasks/{task_id}", response_model=api.db.TaskPublic)
async def get_task(
    task: api.dependencies.TaskDep,
):
    return task


@router.patch("/tasks/{task_id}", response_model=api.db.TaskPublic)
async def update_task(
    task: api.dependencies.TaskDep,
    task_update: api.db.TaskUpdate,
    session: api.dependencies.SessionDep,
):
    column = session.get(api.db.Column, task.column_id)
    if column is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error")

    if task_update.position is not None:
        validate_new_position(column, task_update.position, session)
    if task_update.assignee_id is not None:
        validate_new_assignee(column, task_update.assignee_id, session)

    task.sqlmodel_update(task_update.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task: api.dependencies.TaskDep,
    session: api.dependencies.SessionDep,
):
    session.delete(task)
    session.commit()
