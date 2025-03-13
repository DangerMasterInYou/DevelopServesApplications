from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class RoleResourceDTO(BaseModel):
    id: int
    name: str
    description: str
    cipher: str
    created_at: datetime
    created_by: int
    deleted: bool
    updated_at: Optional[datetime]
    updated_by: Optional[int]

    class Config:
        from_attributes = True
        model_validate = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def to_dict(self):
        return self.model_dump(mode="json")


class RolesResourceDTO(BaseModel):
    roles: List[RoleResourceDTO]

    class Config:
        from_attributes = True
        model_validate = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def to_dict(self):
        return self.model_dump(mode="json")
