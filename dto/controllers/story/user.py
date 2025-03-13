from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database.connect import SessionDep
from database.models.users import UserModel
from dto.resources.user import UserResourceDTO, UserFullResourceDTO
from service.logs import get_change_logs, create_log


async def user_story(changed_id: int, session: SessionDep):
    table_name = "users"
    return await get_change_logs(table_name=table_name, changed_id=changed_id, session=session)


async def revert_user(data: UserFullResourceDTO, created_by: int, session: SessionDep):
    try:
        existing_user = await session.execute(
            select(UserModel).filter(
                (UserModel.username == data.username) | (UserModel.email == data.email)
            )
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="User with this name or cipher already exists")

        new_user = UserModel(
            id=data.id,
            username=data.username,
            password=data.password,
            email=data.email,
            birthday=data.birthday
        )
        session.add(new_user)
        await session.flush()

        after_data = UserFullResourceDTO.model_validate(new_user).model_dump(mode="json")
        await create_log(new_user.__tablename__, new_user.id, created_by, session, None, after_data)

        await session.refresh(new_user)
        return new_user

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def reset_user(data: UserResourceDTO, updated_by: int, session: SessionDep):
    try:
        user = await session.get(UserModel, data.id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        existing_user = await session.execute(
            select(UserModel).filter(
                ((UserModel.username == data.username) | (UserModel.email == data.email)) &
                (UserModel.id != data.id)
            )
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="User with this name or cipher already exists")

        before_data = UserResourceDTO.model_validate(user).model_dump(mode="json")

        user.username = data.name
        user.password = data.password
        user.email = data.email
        user.birthday = data.birthday

        await session.commit()
        await session.refresh(user)

        after_data = UserResourceDTO.model_validate(user).model_dump(mode="json")
        await create_log(user.__tablename__, user.id, updated_by, session, before_data, after_data)

        return user

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


async def update_story_user(user_id: int, data: UserFullResourceDTO, creator_by: int, session: SessionDep):
    try:
        user = await session.get(UserModel, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        name_check_query = await session.execute(
            select(UserModel).filter(UserModel.username == data.username, UserModel.id != user_id)
        )
        if name_check_query.scalars().first():
            raise HTTPException(status_code=400, detail="Username already exists")

        cipher_check_query = await session.execute(
            select(UserModel).filter(UserModel.email == data.email, UserModel.id != user_id)
        )
        if cipher_check_query.scalars().first():
            raise HTTPException(status_code=400, detail="Email already exists")
        before_data = UserFullResourceDTO.model_validate(user).model_dump(mode="json")

        user.username = data.username
        user.password = data.password
        user.email = data.email
        user.birthday = data.birthday

        after_data = UserFullResourceDTO.model_validate(user).model_dump(mode="json")

        await create_log(user.__tablename__, user_id, creator_by, session, before_data, after_data)

        await session.refresh(user)

        return user

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
