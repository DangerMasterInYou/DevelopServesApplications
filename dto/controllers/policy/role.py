from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from database.connect import SessionDep
from database.models.changeLogs import ChangeLogModel
from database.models.models import RoleModel
from dto.requests.policy.role import CreateRoleRequestDTO, UpdateRoleRequestDTO
from dto.resources.policy.role import RoleResourceDTO
from service.logs import create_log


async def users_roles(session: SessionDep):
    query = await session.execute(
        select(RoleModel)
    )
    return query.scalars().all()


async def create_role(data: CreateRoleRequestDTO, created_by: int, session: SessionDep):
    try:
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

        after_data = RoleResourceDTO.model_validate(new_role).model_dump(mode="json")
        await create_log(new_role.__tablename__, new_role.id, created_by, session, None, after_data)

        await session.commit()
        await session.refresh(new_role)
        return new_role
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def specific_role(role_id: int, session: SessionDep):
    query = await session.execute(select(RoleModel).filter(RoleModel.id == role_id))
    role = query.scalar_one_or_none()
    if role is None:
        raise HTTPException(status_code=400, detail="Role not already exists")

    return role


async def update_role(role_id: int, data: UpdateRoleRequestDTO, updater_id: int, session: SessionDep):
    try:
        table_name = "roles"
        role = await session.get(RoleModel, role_id)
        if not role:
            query = await session.execute(
                select(ChangeLogModel)
                .filter(ChangeLogModel.changed_id == role_id, ChangeLogModel.changed_table == table_name)
            )
            change_log = query.scalars().all()

            if change_log:
                name_exists = await session.scalar(
                    select(RoleModel).where(RoleModel.name == change_log.data_after["name"])
                )
                cipher_exists = await session.scalar(
                    select(RoleModel).where(RoleModel.cipher == change_log.data_after["cipher"])
                )

                if name_exists or cipher_exists:
                    raise HTTPException(status_code=400, detail="Restoration failed: Name or cipher already exists")

                restored_role = RoleModel(
                    id=role_id,
                    name=change_log.data_after["name"],
                    description=change_log.data_after["description"],
                    cipher=change_log.data_after["cipher"],
                    created_by=updater_id,
                    deleted=False
                )

                session.add(restored_role)
                restored_role_dict = RoleResourceDTO.model_validate(restored_role).model_dump(mode="json")

                await create_log(table_name, role_id, updater_id, session, change_log.data_before, restored_role_dict)
                await session.commit()
                return restored_role
            else:
                raise HTTPException(status_code=404, detail="Role not found and no prior data exists")

        name_exists = await session.scalar(
            select(RoleModel).where(RoleModel.name == data.name, RoleModel.id != role_id)
        )
        if name_exists:
            raise HTTPException(status_code=400, detail="Name already exists")

        cipher_exists = await session.scalar(
            select(RoleModel).where(RoleModel.cipher == data.cipher, RoleModel.id != role_id)
        )
        if cipher_exists:
            raise HTTPException(status_code=400, detail="Cipher already exists")

        if role.deleted:
            role.deleted = False

        before_data = RoleResourceDTO.model_validate(role).model_dump(mode="json")

        role.name = data.name
        role.description = data.description
        role.cipher = data.cipher
        role.updated_by = updater_id

        await session.flush()
        after_data = RoleResourceDTO.model_validate(role).model_dump(mode="json")
        await create_log(table_name, role.id, updater_id, session, before_data, after_data)

        await session.commit()
        await session.refresh(role)
        return role

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def hard_delete_role(permission_id: int, updated_by: int, session: SessionDep):
    try:
        permission = await session.get(RoleModel, permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        before_data = RoleResourceDTO.model_validate(permission).model_dump(mode="json")

        await session.delete(permission)
        await session.flush()

        await create_log(permission.__tablename__, permission_id, updated_by, session, before_data, None)

        await session.commit()
        return permission

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def soft_delete_role(permission_id: int, updated_by: int, session: SessionDep):
    try:
        permission = await session.get(RoleModel, permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        before_data = RoleResourceDTO.model_validate(permission).model_dump(mode="json")

        permission.deleted = True
        permission.updated_by = updated_by

        await session.flush()

        after_data = RoleResourceDTO.model_validate(permission).model_dump(mode="json")

        await create_log(permission.__tablename__, permission.id, updated_by, session, before_data, after_data)

        await session.commit()
        await session.refresh(permission)
        return permission

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def restore_role(permission_id: int, updated_by: int, session: SessionDep):
    try:
        permission = await session.get(RoleModel, permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        before_data = RoleResourceDTO.model_validate(permission).model_dump(mode="json")

        permission.deleted = False
        permission.updated_by = updated_by

        await session.flush()

        after_data = RoleResourceDTO.model_validate(permission).model_dump(mode="json")

        await create_log(permission.__tablename__, permission.id, updated_by, session, before_data, after_data)

        await session.commit()
        await session.refresh(permission)
        return permission

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
