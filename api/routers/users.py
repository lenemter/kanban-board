from fastapi import APIRouter

import api.db
import api.dependencies
import api.utils

router = APIRouter(tags=["users"])


@router.get("/users/me", response_model=api.db.UserPublic)
async def get_user_me(
    current_user: api.dependencies.CurrentUserDep
):
    return current_user


@router.patch("/users/me", response_model=api.db.UserPublic)
async def edit_user_me(
    user_update: api.db.UserUpdate,
    current_user: api.dependencies.CurrentUserDep,
    session: api.dependencies.SessionDep,
):
    to_update = user_update.model_dump(exclude_unset=True, exclude={"password"})

    if user_update.password is not None:
        to_update["hashed_password"] = api.utils.get_password_hash(user_update.password)

    current_user.sqlmodel_update(to_update)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user
