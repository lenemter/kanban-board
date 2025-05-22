from fastapi import APIRouter, HTTPException, status

import api.db
import api.dependencies
import api.schemas
import api.utils

router = APIRouter(tags=["users"])


@router.get("/users/me", response_model=api.schemas.UserPublic)
async def get_user_me(current_user: api.dependencies.CurrentUserDep):
    return current_user


@router.get("/users/{user_id}", response_model=api.schemas.UserPublic)
async def get_user(_: api.dependencies.CurrentUserDep, user_id: int):
    user = api.db.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    return user


@router.patch("/users/me", response_model=api.schemas.UserPublic)
async def edit_user_me(
    current_user: api.dependencies.CurrentUserDep,
    user_update: api.schemas.UserUpdate,
    session: api.dependencies.SessionDep,
):
    to_update = user_update.model_dump(exclude_unset=True, exclude={"password"})

    if not isinstance(user_update.password, api.schemas.UnsetType):
        to_update["hashed_password"] = api.utils.get_password_hash(user_update.password)

    return api.db.update_user(session, current_user, to_update)
