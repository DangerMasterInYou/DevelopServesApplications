from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class PermissionResourceDTO(BaseModel):
    id: int
    name: str
    description: str
    cipher: str
    created_at: datetime
    created_by: int
    deleted: bool
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class PermissionsResourceDTO(BaseModel):
    permissions: List[PermissionResourceDTO]

    class Config:
        from_attributes = True
