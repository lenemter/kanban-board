from typing import TYPE_CHECKING, Any

from sqlmodel import Session, select

if TYPE_CHECKING:
    from .. import Board, Column


def get_columns(board: Board) -> list[Column]:
    from .. import engine, Column

    with Session(engine) as session:
        return list(
            session.exec(
                select(Column).where(
                    Column.board_id == board.id
                )
            ).all()
        )


def create_column(**kwargs) -> Column:
    from .. import engine, Column

    with Session(engine) as session:
        new_column = Column(**kwargs)
        session.add(new_column)
        session.commit()
        session.refresh(new_column)

        return new_column


def update_column(column: Column, update: dict[str, Any]) -> Column:
    from .. import engine

    with Session(engine) as session:
        column.sqlmodel_update(update)
        session.add(column)
        session.commit()
        session.refresh(column)

        return column


def delete_column(column: Column) -> None:
    from .. import engine

    with Session(engine) as session:
        session.delete(column)
        session.commit()
