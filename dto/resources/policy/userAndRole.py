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
        model_validate = True


class UserAndRolesResourceDTO(BaseModel):
    user_and_roles: List[UserAndRoleResourceDTO]

    class Config:
        model_validate = True
