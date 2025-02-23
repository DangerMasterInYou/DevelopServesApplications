from fastapi import HTTPException
from sqlalchemy.future import select

from database.connect import SessionDep
from database.models.models import RoleModel
from dto.requests.policy.role import CreateRoleRequestDTO, UpdateRoleRequestDTO


async def users_roles(session: SessionDep):
    query = await session.execute(
        select(RoleModel)
    )
    return query.scalars().all()


async def create_role(data: CreateRoleRequestDTO, session: SessionDep, created_by: int):
    existing_role = await session.execute(
        select(RoleModel).filter((RoleModel.name == data.name) | (RoleModel.cipher == data.cipher))
    )
    if existing_role.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Role with this name or cipher already exists")

    new_role = RoleModel(
        name=data.name,
        description=data.description,
        cipher=data.cipher,
        created_by=created_by
    )

    session.add(new_role)
    await session.flush()
    await session.commit()
    await session.refresh(new_role)

    return new_role


async def specific_role(role_id: int, session: SessionDep):
    query = await session.execute(select(RoleModel).filter(RoleModel.id == role_id))
    role = query.scalar_one_or_none()
    if role is None:
        raise HTTPException(status_code=400, detail="Role not already exists")

    return role


async def update_role(role_id: int, data: UpdateRoleRequestDTO, updater_id: int,  session: SessionDep):
    role = await session.get(RoleModel, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    name_check_query = await session.execute(
        select(RoleModel).filter(RoleModel.name == data.name, RoleModel.id != RoleModel)
    )
    name_exists = name_check_query.scalars().first()
    if name_exists:
        raise HTTPException(status_code=400, detail="Name already exists")
    cipher_check_query = await session.execute(
        select(RoleModel).filter(RoleModel.cipher == data.cipher, RoleModel.id != RoleModel)
    )
    cipher_exists = cipher_check_query.scalars().first()
    if cipher_exists:
        raise HTTPException(status_code=400, detail="Cipher already exists")

    role.name = data.name
    role.description = data.description
    role.cipher = data.cipher
    role.updated_by = updater_id

    await session.commit()
    await session.refresh(role)

    return role


async def hard_delete_role(role_id: int,  session: SessionDep):
    role = await session.get(RoleModel, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    await session.delete(role)
    await session.commit()

    return role


async def soft_delete_role(role_id: int, updater_id: int,  session: SessionDep):
    role = await session.get(RoleModel, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    role.deleted = True
    role.updated_by = updater_id

    await session.commit()
    await session.refresh(role)

    return role


async def restore_role(role_id: int, updater_id: int,  session: SessionDep):
    role = await session.get(RoleModel, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    role.deleted = False
    role.updated_by = updater_id

    await session.commit()
    await session.refresh(role)

    return role
