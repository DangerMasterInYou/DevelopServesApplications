from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database.connect import SessionDep
from database.models.policy.permissions import PermissionModel
from dto.resources.policy.permission import PermissionResourceDTO
from service.logs import get_change_logs, create_log
from service.parse_datetime import parse_datetime


async def permission_story(changed_id: int, session: SessionDep):
    table_name = "permissions"
    return await get_change_logs(table_name=table_name, changed_id=changed_id, session=session)


async def revert_permission(data: PermissionResourceDTO, created_by: int, session: SessionDep):
    try:
        existing_permission = await session.execute(
            select(PermissionModel).filter(
                (PermissionModel.name == data.name) | (PermissionModel.cipher == data.cipher)
            )
        )
        if existing_permission.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Permission with this name or cipher already exists")

        new_permission = PermissionModel(
            id=data.id,
            name=data.name,
            description=data.description,
            cipher=data.cipher,
            created_at=parse_datetime(data.created_at),
            created_by=data.created_by,
            deleted=data.deleted,
            updated_at=parse_datetime(data.updated_at),
            updated_by=data.updated_by
        )
        session.add(new_permission)
        await session.flush()

        after_data = PermissionResourceDTO.model_validate(new_permission).model_dump(mode="json")
        await create_log(new_permission.__tablename__, new_permission.id, created_by, session, None, after_data)

        await session.refresh(new_permission)
        return new_permission

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def reset_permission(data: PermissionResourceDTO, updated_by: int, session: SessionDep):
    try:
        permission = await session.get(PermissionModel, data.id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        existing_permission = await session.execute(
            select(PermissionModel).filter(
                ((PermissionModel.name == data.name) | (PermissionModel.cipher == data.cipher)) &
                (PermissionModel.id != data.id)
            )
        )
        if existing_permission.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Permission with this name or cipher already exists")

        before_data = PermissionResourceDTO.model_validate(permission).model_dump(mode="json")

        permission.name = data.name
        permission.description = data.description
        permission.cipher = data.cipher
        permission.created_at = parse_datetime(data.сreated_at),
        permission.created_by = data.created_by
        permission.deleted = data.deleted
        permission.updated_at = parse_datetime(data.updated_at),
        permission.updated_by = updated_by

        await session.commit()
        await session.refresh(permission)

        after_data = PermissionResourceDTO.model_validate(permission).model_dump(mode="json")
        await create_log(permission.__tablename__, permission.id, updated_by, session, before_data, after_data)

        return permission

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


async def update_story_permission(permission_id: int, data: PermissionResourceDTO, creator_by: int, session: SessionDep):
    try:
        permission = await session.get(PermissionModel, permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        name_check_query = await session.execute(
            select(PermissionModel).filter(PermissionModel.name == data.name, PermissionModel.id != permission_id)
        )
        if name_check_query.scalars().first():
            raise HTTPException(status_code=400, detail="Name already exists")

        cipher_check_query = await session.execute(
            select(PermissionModel).filter(PermissionModel.cipher == data.cipher, PermissionModel.id != permission_id)
        )
        if cipher_check_query.scalars().first():
            raise HTTPException(status_code=400, detail="Cipher already exists")

        before_data = PermissionResourceDTO.model_validate(permission).model_dump(mode="json")

        permission.name = data.name
        permission.description = data.description
        permission.cipher = data.cipher
        permission.updated_by = creator_by

        after_data = PermissionResourceDTO.model_validate(permission).model_dump(mode="json")

        await create_log(permission.__tablename__, permission_id, creator_by, session, before_data, after_data)

        await session.refresh(permission)

        return permission

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
