import json
from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError
from database.connect import SessionDep
from database.models.changeLogs import ChangeLogModel
from dto.controllers.policy.permission import hard_delete_permission
from dto.controllers.policy.role import hard_delete_role
from dto.controllers.story.permission import revert_permission, update_story_permission
from dto.controllers.story.role import revert_role, update_story_role
from dto.controllers.story.user import revert_user, update_story_user
from dto.controllers.user import hard_delete_user
from dto.resources.policy.permission import PermissionResourceDTO
from dto.resources.policy.role import RoleResourceDTO
from dto.resources.user import UserFullResourceDTO
from service.logs import get_change_logs


async def revert_story(story_id: int, updater_id: int, session: SessionDep):
    try:
        query = await session.execute(
            select(ChangeLogModel)
            .filter(ChangeLogModel.id == story_id,
                    or_(
                        ChangeLogModel.data_after.is_not(None),
                        ChangeLogModel.data_before.is_not(None)
                    ))
        )
        change_log = query.scalar_one_or_none()

        if not change_log:
            raise HTTPException(status_code=404, detail="Change log entry not found")

        table_name = change_log.changed_table
        data_before_json = json.loads(change_log.data_before) if isinstance(change_log.data_before, str) else change_log.data_before if isinstance(change_log.data_before, dict) else None
        data_after_json = json.loads(change_log.data_after) if isinstance(change_log.data_after, str) else change_log.data_after if isinstance(change_log.data_after, dict) else None
        entity_id = change_log.changed_id

        if data_before_json is None:
            if table_name == "permissions":
                await hard_delete_permission(entity_id, updater_id, session)
            elif table_name == "roles":
                await hard_delete_role(entity_id, updater_id, session)
            elif table_name == "users":
                await hard_delete_user(entity_id, session, updater_id)
        elif data_after_json is None:
            if table_name == "permissions":
                data_before = PermissionResourceDTO(**data_before_json) if data_before_json is not None else None
                await revert_permission(data_before, updater_id, session)
            elif table_name == "roles":
                data_before = RoleResourceDTO(**data_before_json) if data_before_json is not None else None
                await revert_role(data_before, updater_id, session)
            elif table_name == "users":
                data_before = UserFullResourceDTO(**data_before_json) if data_before_json is not None else None
                await revert_user(data_before, updater_id, session)
        else:
            if table_name == "permissions":
                data_before = PermissionResourceDTO(**data_before_json) if data_before_json is not None else None
                await update_story_permission(entity_id, data_before, updater_id, session)
            elif table_name == "roles":
                data_before = RoleResourceDTO(**data_before_json) if data_before_json is not None else None
                await update_story_role(entity_id, data_before, updater_id, session)
            elif table_name == "users":
                data_before = UserFullResourceDTO(**data_before_json) if data_before_json is not None else None
                await update_story_user(entity_id, data_before, updater_id, session)

        await session.commit()
        return await get_change_logs(table_name, entity_id, session)
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


