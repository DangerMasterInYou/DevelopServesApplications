from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from database.connect import SessionDep
from database.models.policy.permissions import PermissionModel
from service.logs import create_log
from dto.requests.policy.permission import UpdatePermissionRequestDTO, CreatePermissionRequestDTO
from dto.resources.policy.permission import PermissionResourceDTO


async def permissions(session: SessionDep):
    query = await session.execute(
        select(PermissionModel)
    )
    _permissions = query.scalars().all()

    if not _permissions:
        raise HTTPException(status_code=403, detail="You do not have any permissions")

    return _permissions


async def create_permission(data: CreatePermissionRequestDTO, created_by: int, session: SessionDep):
    try:
        existing_permission = await session.execute(
            select(PermissionModel).filter(
                (PermissionModel.name == data.name) | (PermissionModel.cipher == data.cipher)
            )
        )
        if existing_permission.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Permission with this name or cipher already exists")

        new_permission = PermissionModel(
            name=data.name,
            description=data.description,
            cipher=data.cipher,
            created_by=created_by
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


async def specific_permission(permission_id: int, session: SessionDep):
    query = await session.execute(select(PermissionModel).filter(PermissionModel.id == permission_id))
    permission = query.scalar_one_or_none()
    if permission is None:
        raise HTTPException(status_code=400, detail="Permission not already exists")

    return permission


async def update_permission(permission_id: int, data: UpdatePermissionRequestDTO, creator_by: int, session: SessionDep):
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

        await session.commit()
        await session.refresh(permission)

        return permission

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


async def hard_delete_permission(permission_id: int, updated_by: int, session: SessionDep):
    try:
        permission = await session.get(PermissionModel, permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        before_data = PermissionResourceDTO.model_validate(permission).model_dump(mode="json")

        await session.delete(permission)
        await session.flush()

        await create_log(permission.__tablename__, permission_id, updated_by, session, before_data, None)

        await session.commit()
        return permission

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def soft_delete_permission(permission_id: int, updated_by: int, session: SessionDep):
    try:
        permission = await session.get(PermissionModel, permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        before_data = PermissionResourceDTO.model_validate(permission).model_dump(mode="json")

        permission.deleted = True
        permission.updated_by = updated_by

        await session.flush()

        after_data = PermissionResourceDTO.model_validate(permission).model_dump(mode="json")

        await create_log(permission.__tablename__, permission.id, updated_by, session, before_data, after_data)

        await session.commit()
        await session.refresh(permission)
        return permission

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def restore_permission(permission_id: int, updated_by: int, session: SessionDep):
    try:
        permission = await session.get(PermissionModel, permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        before_data = PermissionResourceDTO.model_validate(permission).model_dump(mode="json")

        permission.deleted = False
        permission.updated_by = updated_by

        await session.flush()

        after_data = PermissionResourceDTO.model_validate(permission).model_dump(mode="json")

        await create_log(permission.__tablename__, permission.id, updated_by, session, before_data, after_data)

        await session.commit()
        await session.refresh(permission)
        return permission

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
