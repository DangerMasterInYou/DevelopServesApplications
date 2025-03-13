from typing import List
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from database.connect import SessionDep
from database.models.changeLogs import ChangeLogModel
from dto.resources.changeLog import ChangeLogsDTO, ChangeLogDTO


async def create_log(table_name: str, changed_id: int, updated_by: int, session: SessionDep, before_data: dict = None,
                     after_data: dict = None):

    new_log = ChangeLogModel(
        changed_table=table_name,
        changed_id=changed_id,
        data_before=before_data,
        data_after=after_data,
        updated_by=updated_by
    )
    session.add(new_log)


async def get_change_logs(table_name: str, changed_id: int, session: SessionDep) -> ChangeLogsDTO:
    try:
        result = await session.execute(
            select(ChangeLogModel).where(
                ChangeLogModel.changed_table == table_name,
                ChangeLogModel.changed_id == changed_id
            )
        )
        change_logs = result.scalars().all()

        logs: List[ChangeLogDTO] = []
        for log in change_logs:
            before_data = log.data_before if isinstance(log.data_before, dict) else None
            after_data = log.data_after if isinstance(log.data_after, dict) else None

            filtered_before_data = {}
            filtered_after_data = {}

            # Фильтруем только измененные поля (учитываем None)
            if before_data or after_data:
                all_keys = set((before_data or {}).keys()) | set((after_data or {}).keys())

                for key in all_keys:
                    old_value = before_data.get(key) if before_data else None
                    new_value = after_data.get(key) if after_data else None

                    if old_value != new_value:
                        filtered_before_data[key] = old_value
                        filtered_after_data[key] = new_value

            log_entry = ChangeLogDTO(
                id=log.id,
                changed_table=log.changed_table,
                changed_id=log.changed_id,
                data_before=filtered_before_data if filtered_before_data else None,
                data_after=filtered_after_data if filtered_after_data else None,
                updated_at=log.updated_at,
                updated_by=log.updated_by
            )
            logs.append(log_entry)

        return ChangeLogsDTO(logs=logs)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

