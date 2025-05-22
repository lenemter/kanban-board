from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

import api.db
import api.dependencies
import api.schemas

router = APIRouter(tags=["tasks"])


def validate_new_column(board: api.db.Board, new_column_id: int, session: Session) -> api.db.Column:
    new_column = session.get(api.db.Column, new_column_id)
    if new_column is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Column not found")

    if new_column.board_id != board.id:
        raise HTTPException(status.HTTP_409_CONFLICT, "Cannot move tasks between boards")

    return new_column


def validate_new_position(column: api.db.Column, new_position: int):
    if new_position < 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "Position must be greater or equal 0")

    for task in api.db.get_tasks(column):
        if task.position == new_position:
            raise HTTPException(status.HTTP_409_CONFLICT, "This position is already taken")


def validate_new_assignee(board: api.db.Board, assignee_id: int | None) -> api.db.User | None:
    if assignee_id is None:
        return None

    assigned_user = api.db.get_user_by_id(assignee_id)
    if assigned_user is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "This user doesn't exist")

    if not api.dependencies.check_user_access(assigned_user, board):
        raise HTTPException(status.HTTP_409_CONFLICT, "This user doesn't have access to this board")

    return assigned_user


@router.get("/columns/{column_id}/tasks/", response_model=list[api.schemas.TaskPublic])
async def get_tasks(
    board_and_column: api.dependencies.BoardColumnDep,
    filter: api.schemas.TaskFilter = Depends(),
):
    _, column = board_and_column

    # HTTP cannot serialize null value, so treat string "null" as null value
    if filter.assignee_id == "null":
        filter.assignee_id = None

    # model_dump(exclude_unset=True) is broken with Depends()
    model_dump = {k: v for k, v in filter.model_dump().items() if not isinstance(v, api.schemas.UnsetType)}

    return api.db.get_tasks(column, model_dump)


@router.post("/columns/{column_id}/tasks/", status_code=status.HTTP_201_CREATED, response_model=api.schemas.TaskPublic)
async def add_task(
    board_and_column: api.dependencies.BoardColumnDep,
    task_create: api.schemas.TaskCreate,
    current_user: api.dependencies.CurrentUserDep,
):
    board, column = board_and_column

    validate_new_position(column, task_create.position)
    validate_new_assignee(board, task_create.assignee_id)

    return api.db.create_task(column_id=column.id, created_by=current_user.id, **task_create.model_dump())


@router.get("/tasks/{task_id}", response_model=api.schemas.TaskPublic)
async def get_task(board_column_and_task: api.dependencies.BoardColumnTaskDep):
    _, _, task = board_column_and_task
    return task


@router.patch("/tasks/{task_id}", response_model=api.schemas.TaskPublic)
async def update_task(
    board_column_and_task: api.dependencies.BoardColumnTaskDep,
    task_update: api.schemas.TaskUpdate,
    session: api.dependencies.SessionDep,
):
    board, column, task = board_column_and_task

    if not isinstance(task_update.column_id, api.schemas.UnsetType) and task.column_id != task_update.column_id:
        new_column = validate_new_column(board, task_update.column_id, session)

        api.db.create_task_log(
            task,
            content=f"Moved from {column.name} to {new_column.name}",
        )

    if not isinstance(task_update.position, api.schemas.UnsetType) and task_update.position != task.position:
        validate_new_position(column, task_update.position)

    if not isinstance(task_update.name, api.schemas.UnsetType) and task.name != task_update.name:
        api.db.create_task_log(
            task,
            content=f"~~{task.name}~~ {task_update.name}",
        )

    if not isinstance(task_update.assignee_id, api.schemas.UnsetType) and task.assignee_id != task_update.assignee_id:
        old_assigned_user = api.db.get_user_by_id(task.assignee_id)
        if old_assigned_user is not None:
            api.db.create_task_log(
                task,
                content=f"Unassigned {old_assigned_user.name}"
            )

        new_assigned_user = validate_new_assignee(board, task_update.assignee_id)
        if new_assigned_user is not None:
            api.db.create_task_log(
                task,
                content=f"Assigned {new_assigned_user.name}",
            )

    return api.db.update_task(task, task_update.model_dump(exclude_unset=True))


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(board_column_and_task: api.dependencies.BoardColumnTaskDep):
    _, _, task = board_column_and_task
    api.db.delete_task(task)


@router.get("/tasks/{task_id}/logs/", response_model=list[api.schemas.TaskLogPublic])
async def get_logs(board_column_and_task: api.dependencies.BoardColumnTaskDep):
    _, _, task = board_column_and_task
    return api.db.get_task_logs(task)
