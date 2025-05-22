from typing import TYPE_CHECKING, Any

from sqlmodel import Session, select

if TYPE_CHECKING:
    from .. import Board, BoardUserAccess, User


def get_owned_boards(user_id: int | None) -> list["Board"]:
    from .. import engine, Board

    with Session(engine) as session:
        return list(
            session.exec(
                select(Board).where(
                    Board.owner_id == user_id
                )
            ).all()
        )


def get_shared_boards(user_id: int | None) -> list["Board"]:
    from .. import engine, Board, BoardUserAccess

    with Session(engine) as session:
        shared = list(
            session.exec(
                select(Board)
                .join(BoardUserAccess)
                .where(BoardUserAccess.user_id == user_id)
            ).all()
        )

        return get_owned_boards(user_id) + shared


def create_board(owner: "User", **kwargs) -> "Board":
    from .. import engine, Board

    with Session(engine) as session:
        new_board = Board(owner_id=owner.id, **kwargs)
        session.add(new_board)
        session.commit()
        session.refresh(new_board)

        return new_board


def update_board(session: Session, board: "Board", update: dict[str, Any]) -> "Board":
    board.sqlmodel_update(update)
    session.add(board)
    session.commit()
    session.refresh(board)

    return board


def delete_board(session: Session, board: "Board") -> None:
    session.delete(board)
    session.commit()


def get_users(board: "Board") -> list["User"]:
    from .. import engine, BoardUserAccess, User

    with Session(engine) as session:
        board_user_accesses = session.exec(
            select(BoardUserAccess).where(
                BoardUserAccess.board_id == board.id
            )
        ).all()

        result: list[Any] = [session.get(User, board.owner_id)]
        for board_user_access in board_user_accesses:
            result.append(session.get(User, board_user_access.user_id))

        return result


def add_user(board: "Board", user_id: int) -> "BoardUserAccess":
    from .. import engine, BoardUserAccess

    with Session(engine) as session:
        old_board_user_access = session.exec(
            select(BoardUserAccess).where(
                BoardUserAccess.board_id == board.id,
                BoardUserAccess.user_id == user_id
            )
        ).first()

        if old_board_user_access is not None:
            return old_board_user_access

        board_user_access = BoardUserAccess(board_id=board.id, user_id=user_id)
        session.add(board_user_access)
        session.commit()
        session.refresh(board_user_access)

        return board_user_access


def remove_user(board: "Board", user_id: int) -> None:
    from .. import engine, BoardUserAccess

    with Session(engine) as session:
        board_user_access = session.exec(
            select(BoardUserAccess).where(
                BoardUserAccess.board_id == board.id,
                BoardUserAccess.user_id == user_id
            )
        ).first()

        if board_user_access is None:
            return

        session.delete(board_user_access)
        session.commit()
