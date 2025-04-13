from fastapi import APIRouter, status
from sqlmodel import select

import api.db
import api.dependencies

router = APIRouter(tags=["tasks"])


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
    session: api.dependencies.SessionDep,
):
    task = api.db.Task(column_id=column.id, **task_create.model_dump())
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
