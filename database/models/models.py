from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from database.models.users import UserModel
from database.models.tokens import TokenModel
from database.models.policy.roles import RoleModel
from database.models.policy.permissions import PermissionModel
from database.models.policy.usersAndRoles import UserAndRoleModel
from database.models.policy.rolesAndPermissions import RoleAndPermissionModel

__all__ = ["UserModel", "TokenModel", "RoleModel", "PermissionModel", "UserAndRoleModel", "RoleAndPermissionModel"]
