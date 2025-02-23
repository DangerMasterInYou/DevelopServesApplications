from database.models.policy.roles import RoleModel
import os
from dotenv import load_dotenv

load_dotenv()

admin_id = os.getenv("ADMIN_ID")

admin_roles = RoleModel(name="Administrator", description="Administrator role", cipher="admin", created_by=admin_id)
user_roles = RoleModel(name="User", description="User role", cipher="user", created_by=admin_id)
guest_roles = RoleModel(name="Guest", description="Guest role", cipher="guest", created_by=admin_id)

roles_list = [admin_roles, user_roles, guest_roles]
