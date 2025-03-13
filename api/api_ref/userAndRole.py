from enum import Enum
from fastapi import APIRouter, Depends
from starlette import status
from database.connect import SessionDep
from dto.controllers.policy.userAndRole import user_add_roles, hard_delete_user_role, user_roles, soft_delete_user_role, restore_user_role
from dto.controllers.story.user import user_story
from dto.controllers.user import users
from dto.resources.policy.role import RoleResourceDTO, RolesResourceDTO
from dto.resources.policy.userAndRole import UserAndRolesResourceDTO, UserAndRoleResourceDTO
from dto.resources.user import UsersResourceDTO, UserResourceDTO
from service.jwt_token import jwt_checker
from service.policy import check_policy_role_to_permission, AbstractPermissionCipher

api_ref_user = APIRouter(prefix="/user")


class UserPermissionCipher(Enum):
    type = "user"
    get_list = AbstractPermissionCipher.get_list.value + type
    read = AbstractPermissionCipher.read.value + type
    create = AbstractPermissionCipher.create.value + type
    update = AbstractPermissionCipher.update.value + type
    delete = AbstractPermissionCipher.delete.value + type
    restore = AbstractPermissionCipher.restore.value + type
    get_story = AbstractPermissionCipher.get_story.value + type


@api_ref_user.get('', response_model=UsersResourceDTO, status_code=status.HTTP_200_OK)
async def get_list_users(session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = UserPermissionCipher.get_list.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)

    list_users = await users(session)
    user_dtos = [UserResourceDTO.model_validate(user.__dict__) for user in list_users]

    return UsersResourceDTO(users=user_dtos)


@api_ref_user.get('/{user_id:int}/role', response_model=RolesResourceDTO, status_code=status.HTTP_200_OK)
async def get_user_role(user_id: int, session: SessionDep, payload: str =  Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = UserPermissionCipher.read.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)

    roles = await user_roles(user_id, session)
    role_dtos = [RoleResourceDTO.model_validate(role.__dict__) for role in roles]

    return RolesResourceDTO(roles=role_dtos)


@api_ref_user.post('/{user_id:int}/role', response_model=UserAndRolesResourceDTO, status_code=status.HTTP_200_OK)
async def post_user_add_roles(user_id: int, session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = UserPermissionCipher.create.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)
    roles = await user_add_roles(user_id, int(payload['user_id']), session)
    user_and_roles_dtos = [UserAndRoleResourceDTO.model_validate(role.__dict__) for role in roles]
    return UserAndRolesResourceDTO(user_and_roles=user_and_roles_dtos)


@api_ref_user.delete('/{user_id:int}/role/{role_id:int}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_hard_user_role(user_id: int, role_id: int, session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = UserPermissionCipher.delete.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)
    return await hard_delete_user_role(user_id, role_id, session)


@api_ref_user.delete('/{user_id:int}/role/{role_id:int}/soft', status_code=status.HTTP_200_OK)
async def delete_soft_user_role(session: SessionDep, user_id: int, role_id: int, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = UserPermissionCipher.delete.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)
    return await soft_delete_user_role(role_id, user_id, updater_id, session)


@api_ref_user.post('/{user_id:int}/role/{role_id:int}/restore', status_code=status.HTTP_200_OK)
async def post_user_role_restore(session: SessionDep, user_id: int, role_id: int, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = UserPermissionCipher.restore.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)
    return await restore_user_role(role_id, user_id, updater_id, session)


@api_ref_user.get('/{user_id:int}/story', status_code=status.HTTP_200_OK)
async def get_user_story(session: SessionDep, user_id: int, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = UserPermissionCipher.get_story.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)
    return await user_story(user_id, updater_id, session)
