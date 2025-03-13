from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class ChangeLogDTO(BaseModel):
    id: int
    changed_table: str
    changed_id: int
    data_before: Optional[dict]
    data_after: Optional[dict]
    updated_at: Optional[datetime] = None
    updated_by: int

    class Config:
        model_validate = True


class ChangeLogsDTO(BaseModel):
    logs: List[ChangeLogDTO]

    class Config:
        model_validate = True
