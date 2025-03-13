from fastapi import APIRouter, Depends
from starlette import status

from api.api_ref.policy.permission import PermissionCipher
from api.api_ref.policy.role import RolePermissionCipher
from api.api_ref.userAndRole import UserPermissionCipher
from database.connect import SessionDep
from dto.controllers.story.story import revert_story
from dto.resources.changeLog import ChangeLogsDTO
from service.jwt_token import jwt_checker
from service.policy import check_policy_role_to_permission

story = APIRouter(prefix="/story")


@story.post('', response_model=ChangeLogsDTO, status_code=status.HTTP_200_OK)
async def patch_revert(story_id: int, session: SessionDep, payload: str = Depends(jwt_checker)):
    updater_id = int(payload['user_id'])
    ciphers = [PermissionCipher.update.value, RolePermissionCipher.update.value, UserPermissionCipher.update.value]
    for cipher in ciphers:
        _: bool = await check_policy_role_to_permission(updater_id, cipher, session)

    return await revert_story(story_id, updater_id, session)
