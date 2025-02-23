from enum import Enum
from fastapi import APIRouter, Depends
from starlette import status
from database.connect import SessionDep
from dto.controllers.policy.role import users_roles, create_role, specific_role, update_role, hard_delete_role, \
    soft_delete_role, restore_role
from dto.requests.policy.role import CreateRoleRequestDTO, UpdateRoleRequestDTO
from dto.resources.policy.role import RoleResourceDTO, RolesResourceDTO
from service.jwt_token import jwt_checker
from service.policy import check_policy_role_to_permission, AbstractPermissionCipher

api_ref_policy_role = APIRouter(prefix="/role")


class RolePermissionCipher(Enum):
    type = "role"
    get_list = AbstractPermissionCipher.get_list.value + type
    read = AbstractPermissionCipher.read.value + type
    create = AbstractPermissionCipher.create.value + type
    update = AbstractPermissionCipher.update.value + type
    delete = AbstractPermissionCipher.delete.value + type
    restore = AbstractPermissionCipher.restore.value + type


@api_ref_policy_role.get('', response_model=RolesResourceDTO, status_code=status.HTTP_200_OK)
async def get_roles(session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = RolePermissionCipher.get_list.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)

    roles = await users_roles(session)
    role_dtos = [RoleResourceDTO.model_validate(role.__dict__) for role in roles]

    return RolesResourceDTO(roles=role_dtos)


@api_ref_policy_role.post('', response_model=RoleResourceDTO, status_code=status.HTTP_201_CREATED)
async def post_create_role(data: CreateRoleRequestDTO, session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = RolePermissionCipher.create.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)

    new_role = await create_role(data, updater_id,session)

    return RoleResourceDTO.model_validate(new_role.__dict__)


@api_ref_policy_role.get('/{role_id:int}', response_model=RoleResourceDTO, status_code=status.HTTP_200_OK)
async def get_specific_role(role_id: int, session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = RolePermissionCipher.read.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)
    return await specific_role(role_id, session)


@api_ref_policy_role.put('/{role_id:int}', response_model=RoleResourceDTO, status_code=status.HTTP_200_OK)
async def put_role(role_id: int, data: UpdateRoleRequestDTO, session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = RolePermissionCipher.update.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)

    role = await update_role(role_id, data, updater_id, session)

    return RoleResourceDTO.model_validate(role.__dict__)


@api_ref_policy_role.delete('/{role_id:int}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_hard_role(role_id: int, session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = RolePermissionCipher.delete.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)

    role = await hard_delete_role(role_id, session)


@api_ref_policy_role.delete('/{role_id:int}/soft', response_model=RoleResourceDTO, status_code=status.HTTP_200_OK)
async def delete_soft_role(role_id: int, session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = RolePermissionCipher.delete.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)

    role = await soft_delete_role(role_id, updater_id, session)

    return RoleResourceDTO.model_validate(role.__dict__)


@api_ref_policy_role.post('/{role_id:int}/restore', response_model=RoleResourceDTO, status_code=status.HTTP_200_OK)
async def post_role_restore(role_id: int, session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = RolePermissionCipher.restore.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)

    role = await restore_role(role_id, updater_id, session)

    return RoleResourceDTO.model_validate(role.__dict__)
