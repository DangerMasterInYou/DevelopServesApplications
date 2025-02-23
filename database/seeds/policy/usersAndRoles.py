from sqlalchemy import select
from database.models.models import UserAndRoleModel
from database.models.users import UserModel
from database.models.policy.roles import RoleModel
from database.connect import SessionDep
import os
from dotenv import load_dotenv

load_dotenv()

admin_id = os.getenv("ADMIN_ID")


async def users_and_roles_list_return(session: SessionDep):
    users = (await session.execute(select(UserModel))).scalars().all()
    roles = (await session.execute(select(RoleModel))).scalars().all()

    users_and_roles_list = []
    for user in users:
        for role in roles:
            if role.cipher == "admin" and user.username == "Administrator":
                users_and_roles_list.append(UserAndRoleModel(user_id=user.id, role_id=role.id, created_by=admin_id))
            elif role.cipher == "user" and user.username == "Useruser":
                users_and_roles_list.append(UserAndRoleModel(user_id=user.id, role_id=role.id, created_by=admin_id))
            elif role.cipher == "guest" and user.username == "Guestguest":
                users_and_roles_list.append(UserAndRoleModel(user_id=user.id, role_id=role.id, created_by=admin_id))
    return users_and_roles_list
