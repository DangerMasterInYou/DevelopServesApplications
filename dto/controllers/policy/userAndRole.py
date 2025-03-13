from fastapi import HTTPException
from sqlalchemy.future import select
from database.connect import SessionDep
from database.models.policy.roles import RoleModel
from database.models.policy.usersAndRoles import UserAndRoleModel


async def user_roles(user_id: int, session: SessionDep):
    query = await session.execute(
        select(RoleModel)
        .join(UserAndRoleModel, UserAndRoleModel.role_id == RoleModel.id)
        .filter(UserAndRoleModel.user_id == user_id)
    )
    return query.scalars().all()


async def user_add_roles(user_id: int, creator_id: int, session: SessionDep):
    roles_id = (await session.execute(select(RoleModel.id))).scalars().all()

    query = await session.execute(
        select(UserAndRoleModel)
        .filter(UserAndRoleModel.user_id == user_id)
    )
    before_user_roles = query.scalars().all()

    existing_roles = {role.role_id for role in before_user_roles}

    for role_id in roles_id:
        if role_id in existing_roles:
            for before_user_role in before_user_roles:
                if before_user_role.role_id == role_id and before_user_role.deleted == True:
                    before_user_role.deleted = False
                    before_user_role.updated_by = creator_id
        else:
            user_new_role = UserAndRoleModel(user_id=user_id, role_id=role_id, created_by=creator_id)
            session.add(user_new_role)

    await session.flush()
    await session.commit()

    query = await session.execute(
        select(UserAndRoleModel)
        .filter(UserAndRoleModel.user_id == user_id)
    )

    return query.scalars().all()


async def hard_delete_user_role(user_id: int, role_id: int, session: SessionDep):
    query = await session.execute(
        select(UserAndRoleModel)
        .filter(UserAndRoleModel.user_id == user_id, UserAndRoleModel.role_id == role_id)
    )
    delete_user_roles = query.scalars().all()

    if not delete_user_roles:
        raise HTTPException(status_code=404, detail="User or role not found")

    for user_role in delete_user_roles:
        await session.delete(user_role)

    await session.flush()
    await session.commit()

    return delete_user_roles


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
