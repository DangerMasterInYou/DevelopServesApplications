from typing import List
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class UserAndRoleResourceDTO(BaseModel):
    id: int
    user_id: int
    role_id: int
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


class UserAndRolesResourceDTO(BaseModel):
    user_and_roles: List[UserAndRoleResourceDTO]

    class Config:
        from_attributes = True
        model_validate = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def to_dict(self):
        return self.model_dump(mode="json")
