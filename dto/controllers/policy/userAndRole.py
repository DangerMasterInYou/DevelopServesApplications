from fastapi import HTTPException
from sqlalchemy.future import select
from database.connect import SessionDep
from database.models.policy.roles import RoleModel
from database.models.policy.usersAndRoles import UserAndRoleModel


async def user_add_roles(user_id: int, creator_id: int, session: SessionDep):
    roles_id = (await session.execute(select(RoleModel.id))).scalars().all()

    query = await session.execute(
        select(UserAndRoleModel.role_id)
        .filter(UserAndRoleModel.user_id == user_id)
    )
    before_user_roles_id = query.scalars().all()

    if before_user_roles_id:
        raise HTTPException(status_code=400, detail="User already has roles")

    for role_id in roles_id:
        if role_id in before_user_roles_id:
            continue
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
