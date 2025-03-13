from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from database.connect import SessionDep
from database.models.users import UserModel
from dto.resources.user import UserFullResourceDTO
from service.logs import create_log

table_name = 'users'


async def users(session: SessionDep):
    try:
        query = await session.execute(select(UserModel))
        _users = query.scalars().all()

        if not _users:
            raise HTTPException(status_code=403, detail="You do not have any users")

        return _users

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=504, detail=f"Database error: {str(e)}")


async def hard_delete_user(user_id: int, session: SessionDep, updater_id: int = None):
    try:
        query = await session.execute(
            select(UserModel).filter(UserModel.id == user_id)
        )
        delete_user = query.scalars().first()

        if not delete_user:
            raise HTTPException(status_code=404, detail="User not found")

        before_data = UserFullResourceDTO.model_validate(delete_user).model_dump(mode="json")

        await create_log(table_name, user_id, updater_id, session, before_data, None)

        await session.delete(delete_user)
        await session.commit()

        return delete_user

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=504, detail=f"Database error: {str(e)}")
