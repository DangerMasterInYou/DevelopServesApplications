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
        model_validate = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def to_dict(self):
        return self.model_dump(mode="json")


class PermissionsResourceDTO(BaseModel):
    permissions: List[PermissionResourceDTO]

    class Config:
        from_attributes = True
        model_validate = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def to_dict(self):
        return self.model_dump(mode="json")
