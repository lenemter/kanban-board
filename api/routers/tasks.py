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


def validate_new_assignee(board: api.db.Board, assignee_id: int | None, session: Session) -> api.db.User | None:
    if assignee_id is None:
        return None

    assigned_user = session.get(api.db.User, assignee_id)
    if assigned_user is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "This user doesn't exist")

    if not api.dependencies.check_user_access(assigned_user, board):
        raise HTTPException(status.HTTP_409_CONFLICT, "This user doesn't have access to this board")

    return assigned_user


@router.get("/columns/{column_id}/tasks/", response_model=list[api.db.TaskPublic])
async def get_tasks(
    board_and_column: api.dependencies.BoardColumnDep,
    session: api.dependencies.SessionDep,
):
    _, column = board_and_column
    return list(
        session.exec(
            select(api.db.Task).where(
                api.db.Task.column_id == column.id
            )
        ).all()
    )


@router.post("/columns/{column_id}/tasks/", status_code=status.HTTP_201_CREATED, response_model=api.db.TaskPublic)
async def add_task(
    board_and_column: api.dependencies.BoardColumnDep,
    task_create: api.db.TaskCreate,
    current_user: api.dependencies.CurrentUserDep,
    session: api.dependencies.SessionDep,
):
    board, column = board_and_column

    validate_new_position(column, task_create.position, session)
    if task_create.assignee_id is not api.db.Unset:
        validate_new_assignee(board, task_create.assignee_id, session)

    task = api.db.Task(column_id=column.id, created_by=current_user.id, **task_create.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get("/tasks/{task_id}", response_model=api.db.TaskPublic)
async def get_task(
    board_column_and_task: api.dependencies.BoardColumnTaskDep,
):
    _, _, task = board_column_and_task
    return task


@router.patch("/tasks/{task_id}", response_model=api.db.TaskPublic)
async def update_task(
    board_column_and_task: api.dependencies.BoardColumnTaskDep,
    task_update: api.db.TaskUpdate,
    session: api.dependencies.SessionDep,
):
    board, column, task = board_column_and_task

    if not isinstance(task_update.position, api.db.UnsetType) and task_update.position != task.position:
        validate_new_position(column, task_update.position, session)

    if not isinstance(task_update.name, api.db.UnsetType):
        rename_message = api.db.TaskLog(
            task_id=task.id,
            content=f"~~{task.name}~~ {task_update.name}",
        )
        session.add(rename_message)

    if not isinstance(task_update.assignee_id, api.db.UnsetType):
        if task.assignee_id is not None:
            old_assigned_user = session.get(api.db.User, task.assignee_id)
            if old_assigned_user is not None:
                removed_assignee_message = api.db.TaskLog(
                    task_id=task.id,
                    content=f"Unassigned {old_assigned_user.name}"
                )
                session.add(removed_assignee_message)

        new_assigned_user = validate_new_assignee(board, task_update.assignee_id, session)
        if new_assigned_user is not None:
            new_assignee_message = api.db.TaskLog(
                task_id=task.id,
                content=f"Assigned {new_assigned_user.name}",
            )
            session.add(new_assignee_message)

    task.sqlmodel_update(task_update.model_dump(exclude_unset=True))
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    board_column_and_task: api.dependencies.BoardColumnTaskDep,
    session: api.dependencies.SessionDep,
):
    _, _, task = board_column_and_task
    session.delete(task)
    session.commit()


@router.get("/tasks/{task_id}/logs/", response_model=list[api.db.TaskLogPublic])
async def get_logs(
    board_column_and_task: api.dependencies.BoardColumnTaskDep,
    session: api.dependencies.SessionDep,
):
    _, _, task = board_column_and_task
    return list(
        session.exec(
            select(api.db.TaskLog)
            .where(api.db.TaskLog.task_id == task.id)
        )
    )
