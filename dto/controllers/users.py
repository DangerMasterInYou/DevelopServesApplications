from fastapi import HTTPException
from sqlalchemy.future import select
from database.connect import SessionDep
from database.models.models import UserAndRoleModel, RoleModel
from database.models.users import UserModel


async def users(session: SessionDep):
    query = await session.execute(
        select(UserModel)
    )
    _users = query.scalars().all()

    if not _users:
        raise HTTPException(status_code=403, detail="You do not have any roles")

    return _users


async def user_roles(user_id: int, session: SessionDep):
    query = await session.execute(
        select(RoleModel)
        .join(UserAndRoleModel, UserAndRoleModel.role_id == RoleModel.id)
        .filter(UserAndRoleModel.user_id == user_id)
    )
    return query.scalars().all()


async def soft_delete_user_role(role_id: int, user_id: int, updated_by: int, session: SessionDep):
    query = await session.execute(
        select(UserAndRoleModel).filter(UserAndRoleModel.user_id == user_id, UserAndRoleModel.role_id == role_id)
    )
    _user_roles = query.scalars().all()
    if not _user_roles:
        raise HTTPException(status_code=404, detail="Role not found")

    for user_role in _user_roles:
        user_role.deleted = True
        user_role.updated_by = updated_by
    await session.flush()
    await session.commit()

    return _user_roles


async def restore_user_role(role_id: int, user_id: int, updated_by: int, session: SessionDep):
    query = await session.execute(
        select(UserAndRoleModel).filter(UserAndRoleModel.user_id == user_id, UserAndRoleModel.role_id == role_id)
    )
    _user_roles = query.scalars().all()
    if not _user_roles:
        raise HTTPException(status_code=404, detail="Role not found")

    for user_role in _user_roles:
        user_role.deleted = False
        user_role.updated_by = updated_by
    await session.flush()
    await session.commit()

    return _user_roles
