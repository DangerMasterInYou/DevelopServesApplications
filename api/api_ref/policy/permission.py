from enum import Enum
from fastapi import APIRouter, Depends
from starlette import status
from database.connect import SessionDep
from dto.controllers.policy.permission import permissions, create_permission, specific_permission, update_permission, \
    hard_delete_permission, soft_delete_permission, restore_permission
from dto.controllers.story.permission import permission_story
from dto.requests.policy.permission import UpdatePermissionRequestDTO, CreatePermissionRequestDTO
from dto.resources.changeLog import ChangeLogsDTO
from dto.resources.policy.permission import PermissionsResourceDTO, PermissionResourceDTO
from service.jwt_token import jwt_checker
from service.policy import AbstractPermissionCipher, check_policy_role_to_permission

api_ref_policy_permission = APIRouter(prefix="/permission")


class PermissionCipher(Enum):
    type = "permission"
    get_list = AbstractPermissionCipher.get_list.value + type
    read = AbstractPermissionCipher.read.value + type
    create = AbstractPermissionCipher.create.value + type
    update = AbstractPermissionCipher.update.value + type
    delete = AbstractPermissionCipher.delete.value + type
    restore = AbstractPermissionCipher.restore.value + type
    get_story = AbstractPermissionCipher.get_story.value + type


@api_ref_policy_permission.get('', response_model=PermissionsResourceDTO, status_code=status.HTTP_200_OK)
async def get_permission(session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = PermissionCipher.get_list.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)

    list_permissions = await permissions(session)
    permission_dtos = [PermissionResourceDTO.model_validate(permission.__dict__) for permission in list_permissions]

    return PermissionsResourceDTO(permissions=permission_dtos)


@api_ref_policy_permission.post('', response_model=PermissionResourceDTO,  status_code=status.HTTP_201_CREATED)
async def post_create_permission(data: CreatePermissionRequestDTO, session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = PermissionCipher.create.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)

    new_permission = await create_permission(data, updater_id, session)
    return PermissionResourceDTO.model_validate(new_permission.__dict__)


@api_ref_policy_permission.get('/{permission_id}', response_model=PermissionsResourceDTO, status_code=status.HTTP_200_OK)
async def get_specific_permission(permission_id: int, session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = PermissionCipher.read.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)
    return await specific_permission(permission_id, session)


@api_ref_policy_permission.put('/{permission_id}', status_code=status.HTTP_200_OK)
async def put_permission(permission_id: int, data: UpdatePermissionRequestDTO, session: SessionDep,
                         payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = PermissionCipher.update.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)

    role = await update_permission(permission_id, data, updater_id, session)

    return PermissionResourceDTO.model_validate(role.__dict__)


@api_ref_policy_permission.delete('/{permission_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_hard_permission(permission_id: int, session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = PermissionCipher.delete.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)

    permission = await hard_delete_permission(permission_id, updater_id, session)

    return PermissionResourceDTO.model_validate(permission.__dict__)


@api_ref_policy_permission.delete('/{permission_id}/soft', status_code=status.HTTP_200_OK)
async def delete_soft_permission(permission_id: int, session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = PermissionCipher.delete.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)

    permission = await soft_delete_permission(permission_id, updater_id, session)

    return PermissionResourceDTO.model_validate(permission.__dict__)


@api_ref_policy_permission.post('/{permission_id}/restore', status_code=status.HTTP_200_OK)
async def post_permission_restore(permission_id: int, session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = PermissionCipher.restore.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)

    permission = await restore_permission(permission_id, updater_id, session)

    return PermissionResourceDTO.model_validate(permission.__dict__)


@api_ref_policy_permission.get('/{permission_id:int}/story', response_model=ChangeLogsDTO, status_code=status.HTTP_200_OK)
async def get_permission_story(session: SessionDep, permission_id: int, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    permission_cipher = PermissionCipher.get_story.value
    _: bool = await check_policy_role_to_permission(updater_id, permission_cipher, session)
    return await permission_story(permission_id, session)


