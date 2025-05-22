from typing import TYPE_CHECKING, Any, Union

from sqlmodel import Session, select

if TYPE_CHECKING:
    from .. import Board, Column


def get_columns(board: "Board") -> list["Column"]:
    from .. import engine, Column

    with Session(engine) as session:
        return list(
            session.exec(
                select(Column).where(
                    Column.board_id == board.id
                )
            ).all()
        )


def get_column_by_id(column_id: int) -> Union["Column", None]:
    from .. import engine, Column

    with Session(engine) as session:
        return session.get(Column, column_id)


def create_column(board: "Board", **kwargs) -> "Column":
    from .. import engine, Column

    with Session(engine) as session:
        new_column = Column(board_id=board.id, position=len(get_columns(board)), **kwargs)
        session.add(new_column)
        session.commit()
        session.refresh(new_column)

        return new_column


def update_column(session: Session, column: "Column", update: dict[str, Any]) -> "Column":
    column.sqlmodel_update(update)
    session.add(column)
    session.commit()
    session.refresh(column)

    return column


def delete_column(session: Session, column: "Column") -> None:
    session.delete(column)
    session.commit()
