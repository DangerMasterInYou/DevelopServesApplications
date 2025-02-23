from sqlalchemy import select

from database.models.policy.rolesAndPermissions import RoleAndPermissionModel
from database.models.policy.roles import RoleModel
from database.models.policy.permissions import PermissionModel
from database.connect import SessionDep
import os
from dotenv import load_dotenv

load_dotenv()

admin_id = os.getenv("ADMIN_ID")


async def roles_and_permissions_list_return(session: SessionDep):
    roles = (await session.execute(select(RoleModel))).scalars().all()
    permissions = (await session.execute(select(PermissionModel))).scalars().all()

    roles_and_permissions_list = []
    for role in roles:
        if role.cipher == "admin":
            for permission in permissions:
                roles_and_permissions_list.append(RoleAndPermissionModel(role_id=role.id, permission_id=permission.id,
                                                                         created_by=admin_id))
        elif role.cipher == "user":
            for permission in permissions:
                if permission.cipher in ["get-list-user", "read-user", "update-user"]:
                    roles_and_permissions_list.append(RoleAndPermissionModel(role_id=role.id, permission_id=permission.id,
                                                                             created_by=admin_id))
        elif role.cipher == "guest":
            for permission in permissions:
                if permission.cipher == "get-list-user":
                    roles_and_permissions_list.append(RoleAndPermissionModel(role_id=role.id, permission_id=permission.id,
                                                                             created_by=admin_id))

    return roles_and_permissions_list
