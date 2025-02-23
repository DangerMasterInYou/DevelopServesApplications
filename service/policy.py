from sqlalchemy.future import select
from fastapi import HTTPException
from database.connect import SessionDep
from database.models.models import UserAndRoleModel
from database.models.policy.permissions import PermissionModel
from database.models.policy.rolesAndPermissions import RoleAndPermissionModel
from enum import Enum


class AbstractPermissionCipher(Enum):
    get_list = "get-list-"
    read = "read-"
    create = "create-"
    update = "update-"
    delete = "delete-"
    restore = "restore-"


async def check_policy_role_to_permission(updater_id: int, permission_cipher: str, session: SessionDep) -> (
        bool or HTTPException):
    query = await session.execute(
        select(UserAndRoleModel.role_id).filter(UserAndRoleModel.user_id == updater_id,
                                                UserAndRoleModel.deleted is False)
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
    permission_exists = permission_query.scalars().all()

    if permission_exists:
        return True
    else:
        raise HTTPException(status_code=403, detail=f"You do not have permission: {permission_cipher}")
