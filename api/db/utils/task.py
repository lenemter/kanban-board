from typing import TYPE_CHECKING, Any

from sqlmodel import Session, select

if TYPE_CHECKING:
    from .. import Column, Task, TaskLog


def get_tasks(column: "Column", filter: dict[str, Any]) -> list["Task"]:
    from .. import engine, Task

    with Session(engine) as session:
        return list(
            session.exec(
                select(Task).where(
                    Task.column_id == column.id,
                    *[getattr(Task, field_name) == value for field_name, value in filter.items()]
                )
            ).all()
        )


def create_task(column: "Column", **kwargs) -> "Task":
    from .. import engine, Task

    with Session(engine) as session:
        new_task = Task(column_id=column.id, position=len(get_tasks(column, dict())), **kwargs)
        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        return new_task


def update_task(session: Session, task: "Task", update: dict[str, Any]) -> "Task":
    task.sqlmodel_update(update)
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def delete_task(session: Session, task: "Task") -> None:
    session.delete(task)
    session.commit()


def create_task_log(task: "Task", **kwargs) -> "TaskLog":
    from .. import engine, TaskLog

    with Session(engine) as session:
        new_task = TaskLog(task_id=task.id, **kwargs)
        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        return new_task


def get_task_logs(task: "Task") -> list["TaskLog"]:
    from .. import engine, TaskLog

    with Session(engine) as session:
        return list(
            session.exec(
                select(TaskLog)
                .where(TaskLog.task_id == task.id)
            )
        )
