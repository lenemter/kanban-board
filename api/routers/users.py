from typing import Annotated

from fastapi import APIRouter, Depends
import pydantic

import api.db
import api.dependencies

router = APIRouter(tags=["users"])


class UserResponse(pydantic.BaseModel):
    username: str
    name: str


@router.get("/users/me")
async def read_user_me(
    current_user: Annotated[api.db.User, Depends(api.dependencies.get_current_user)]
) -> UserResponse:
    return UserResponse(**current_user.model_dump())
