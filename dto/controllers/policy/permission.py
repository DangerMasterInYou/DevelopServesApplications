from fastapi import HTTPException
from sqlalchemy.future import select
from database.connect import SessionDep
from database.models.policy.permissions import PermissionModel
from dto.requests.policy.permission import UpdatePermissionRequestDTO, CreatePermissionRequestDTO


async def permissions(session: SessionDep):
    query = await session.execute(
        select(PermissionModel)
    )
    _permissions = query.scalars().all()

    if not _permissions:
        raise HTTPException(status_code=403, detail="You do not have any permissions")

    return _permissions


async def create_permission(data: CreatePermissionRequestDTO, created_by: int, session: SessionDep):
    existing_permission = await session.execute(
        select(PermissionModel).filter((PermissionModel.name == data.name) | (PermissionModel.cipher == data.cipher))
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
    await session.commit()
    await session.refresh(new_permission)

    return new_permission


async def specific_permission(permission_id: int, session: SessionDep):
    query = await session.execute(select(PermissionModel).filter(PermissionModel.id == permission_id))
    permission = query.scalar_one_or_none()
    if permission is None:
        raise HTTPException(status_code=400, detail="Permission not already exists")

    return permission


async def update_permission(permission_id: int, data: UpdatePermissionRequestDTO, creator_by: int,  session: SessionDep):
    permission = await session.get(PermissionModel, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    name_check_query = await session.execute(
        select(PermissionModel).filter(PermissionModel.name == data.name, PermissionModel.id != permission_id)
    )
    name_exists = name_check_query.scalars().first()
    if name_exists:
        raise HTTPException(status_code=400, detail="Name already exists")
    cipher_check_query = await session.execute(
        select(PermissionModel).filter(PermissionModel.cipher == data.cipher, PermissionModel.id != permission_id)
    )
    cipher_exists = cipher_check_query.scalars().first()
    if cipher_exists:
        raise HTTPException(status_code=400, detail="Cipher already exists")

    permission.name = data.name
    permission.description = data.description
    permission.cipher = data.cipher
    permission.updated_by = creator_by

    await session.commit()
    await session.refresh(permission)

    return permission


async def hard_delete_permission(permission_id: int,  session: SessionDep):
    permission = await session.get(PermissionModel, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    await session.delete(permission)
    await session.commit()

    return permission


async def soft_delete_permission(permission_id: int, updated_by: int,  session: SessionDep):
    permission = await session.get(PermissionModel, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    permission.deleted = True
    permission.updated_by = updated_by

    await session.commit()
    await session.refresh(permission)

    return permission


async def restore_permission(permission_id: int, updated_by: int,  session: SessionDep):
    permission = await session.get(PermissionModel, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    permission.deleted = False
    permission.updated_by = updated_by

    await session.commit()
    await session.refresh(permission)

    return permission
