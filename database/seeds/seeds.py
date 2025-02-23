from database.connect import SessionDep
from database.seeds.policy.permissions import permissions_list
from database.seeds.policy.roles import roles_list
from database.seeds.policy.rolesAndPermissions import roles_and_permissions_list_return
from database.seeds.policy.usersAndRoles import users_and_roles_list_return
from database.seeds.users import users_list


async def seeds(session: SessionDep):
    for user in users_list:
        session.add(user)

    for role in roles_list:
        session.add(role)

    for permission in permissions_list:
        session.add(permission)

    roles_and_permissions_list = await roles_and_permissions_list_return(session)
    for role_and_permission in roles_and_permissions_list:
        session.add(role_and_permission)

    users_and_roles_list = await users_and_roles_list_return(session)
    for user_and_role_list in users_and_roles_list:
        session.add(user_and_role_list)

    await session.flush()
    await session.commit()
