from fastapi import APIRouter

import api.dependencies
import api.schemas
import api.utils

router = APIRouter(tags=["users"])


@router.get("/users/me", response_model=api.schemas.UserPublic)
async def get_user_me(
    current_user: api.dependencies.CurrentUserDep
):
    return current_user


@router.patch("/users/me", response_model=api.schemas.UserPublic)
async def edit_user_me(
    user_update: api.schemas.UserUpdate,
    current_user: api.dependencies.CurrentUserDep,
    session: api.dependencies.SessionDep,
):
    to_update = user_update.model_dump(exclude_unset=True, exclude={"password"})

    if not isinstance(user_update.password, api.schemas.UnsetType):
        to_update["hashed_password"] = api.utils.get_password_hash(user_update.password)

    current_user.sqlmodel_update(to_update)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user
