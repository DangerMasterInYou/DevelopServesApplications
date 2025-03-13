from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from database.connect import SessionDep
from database.models.policy.roles import RoleModel
from dto.resources.policy.role import RoleResourceDTO
from service.logs import get_change_logs, create_log
from service.parse_datetime import parse_datetime


async def role_story(changed_id: int, session: SessionDep):
    table_name = "roles"
    return await get_change_logs(table_name=table_name, changed_id=changed_id, session=session)


async def revert_role(data: RoleResourceDTO, created_by: int, session: SessionDep):
    try:
        existing_role = await session.execute(
            select(RoleModel).filter(
                (RoleModel.name == data.name) | (RoleModel.cipher == data.cipher)
            )
        )
        if existing_role.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Role with this name or cipher already exists")

        new_role = RoleModel(
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
        session.add(new_role)
        await session.flush()

        after_data = RoleResourceDTO.model_validate(new_role).model_dump(mode="json")
        await create_log(new_role.__tablename__, new_role.id, created_by, session, None, after_data)

        await session.refresh(new_role)
        return new_role

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def reset_role(data: RoleResourceDTO, updated_by: int, session: SessionDep):
    try:
        role = await session.get(RoleModel, data.id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        existing_role = await session.execute(
            select(RoleModel).filter(
                ((RoleModel.name == data.name) | (RoleModel.cipher == data.cipher)) &
                (RoleModel.id != data.id)
            )
        )
        if existing_role.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Role with this name or cipher already exists")

        before_data = RoleResourceDTO.model_validate(role).model_dump(mode="json")

        role.name = data.name
        role.description = data.description
        role.cipher = data.cipher
        role.created_at = parse_datetime(data.created_at)
        role.created_by = data.created_by
        role.deleted = data.deleted
        role.updated_at = parse_datetime(data.updated_at)
        role.updated_by = updated_by

        await session.commit()
        await session.refresh(role)

        after_data = RoleResourceDTO.model_validate(role).model_dump(mode="json")
        await create_log(role.__tablename__, role.id, updated_by, session, before_data, after_data)

        return role

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


async def update_story_role(role_id: int, data: RoleResourceDTO, creator_by: int, session: SessionDep):
    try:
        role = await session.get(RoleModel, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        name_check_query = await session.execute(
            select(RoleModel).filter(RoleModel.name == data.name, RoleModel.id != role_id)
        )
        if name_check_query.scalars().first():
            raise HTTPException(status_code=400, detail="Name already exists")

        cipher_check_query = await session.execute(
            select(RoleModel).filter(RoleModel.cipher == data.cipher, RoleModel.id != role_id)
        )
        if cipher_check_query.scalars().first():
            raise HTTPException(status_code=400, detail="Cipher already exists")

        before_data = RoleResourceDTO.model_validate(role).model_dump(mode="json")

        role.name = data.name
        role.description = data.description
        role.cipher = data.cipher
        role.updated_by = creator_by

        after_data = RoleResourceDTO.model_validate(role).model_dump(mode="json")
        await create_log(role.__tablename__, role_id, creator_by, session, before_data, after_data)

        await session.refresh(role)

        return role

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
