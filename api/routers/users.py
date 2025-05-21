from fastapi import APIRouter

import api.db
import api.dependencies
import api.schemas
import api.utils

router = APIRouter(tags=["users"])


@router.get("/users/me", response_model=api.schemas.UserPublic)
async def get_user_me(current_user: api.dependencies.CurrentUserDep):
    return current_user


@router.patch("/users/me", response_model=api.schemas.UserPublic)
async def edit_user_me(user_update: api.schemas.UserUpdate, current_user: api.dependencies.CurrentUserDep):
    to_update = user_update.model_dump(exclude_unset=True, exclude={"password"})

    if not isinstance(user_update.password, api.schemas.UnsetType):
        to_update["hashed_password"] = api.utils.get_password_hash(user_update.password)

    return api.db.update_user(current_user, to_update)
