from database.models.policy.permissions import PermissionModel
import os
from dotenv import load_dotenv

load_dotenv()

admin_id = os.getenv("ADMIN_ID")


def type_data_to_model(data: dict, type_permission: str) -> PermissionModel:
    return PermissionModel(name=data["name"]+type_permission, description=data["description"]+type_permission,
                           cipher=data["cipher"]+type_permission, created_by=admin_id)


permissions = [
    {"name": "get-list-", "description": "Get list of ", "cipher": "get-list-"},
    {"name": "read-", "description": "Read ", "cipher": "read-"},
    {"name": "create-", "description": "Create a new ", "cipher": "create-"},
    {"name": "update-", "description": "Update ", "cipher": "update-"},
    {"name": "delete-", "description": "Delete a ", "cipher": "delete-"},
    {"name": "restore-", "description": "Restore a deleted ", "cipher": "restore-"},
    {"name": "get-story-", "description": "Get story of ", "cipher": "get-story-"}
]

user_permissions = [type_data_to_model(perm, "user") for perm in permissions]
role_permissions = [type_data_to_model(perm, "role") for perm in permissions]
permission_permissions = [type_data_to_model(perm, "permission") for perm in permissions]

permissions_list = user_permissions + role_permissions + permission_permissions
