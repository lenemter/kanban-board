from pydantic import BaseModel


class BoardUserAccessPublic(BaseModel):
    board_id: int
    user_id: int
