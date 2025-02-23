from fastapi import HTTPException
from sqlalchemy.future import select
from database.connect import SessionDep
from database.models.models import UserAndRoleModel
from database.models.policy.permissions import PermissionModel
from database.models.policy.rolesAndPermissions import RoleAndPermissionModel


async def get_user_permission(user_id: int, session: SessionDep) -> list[int]:
    roles_id = await check_policy_role_to_permission(user_id, session)
    query = await session.execute(
        select(PermissionModel)
        .join(RoleAndPermissionModel, RoleAndPermissionModel.permission_id == PermissionModel.id)
        .filter(RoleAndPermissionModel.role_id.in_(roles_id))
    )
    return query.scalars().all()


async def check_policy_role_to_permission(user_id: int, permission_cipher: str, session: SessionDep) -> bool or HTTPException:
    query = await session.execute(
        select(UserAndRoleModel.role_id).filter(UserAndRoleModel.user_id == user_id)
    )
    roles_id = query.scalars().all()

    if not roles_id:
        raise HTTPException(status_code=403, detail="You do not have any roles")

    return await check_policy_permission(roles_id, permission_cipher, session)


async def check_policy_permission(roles_id: list[int], permission_cipher: str, session: SessionDep) -> (
        bool or HTTPException):
    if not roles_id:
        raise HTTPException(status_code=403, detail="You do not have any roles")

    permission_query = await session.execute(
        select(RoleAndPermissionModel)
        .join(PermissionModel, RoleAndPermissionModel.permission_id == PermissionModel.id)
        .filter(
            RoleAndPermissionModel.role_id.in_(roles_id),
            PermissionModel.cipher == permission_cipher
        )
    )
    permission_exists = permission_query.scalar_one_or_none()

    if permission_exists:
        return True
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action")