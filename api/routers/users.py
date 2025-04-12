from fastapi import APIRouter

import api.db
import api.dependencies

router = APIRouter(tags=["users"])


@router.get("/users/me", response_model=api.db.UserPublic)
async def read_user_me(current_user: api.dependencies.CurrentUserDep):
    return current_user
