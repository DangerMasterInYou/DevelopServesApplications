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
        model_validate = True


class RolesResourceDTO(BaseModel):
    roles: List[RoleResourceDTO]

    class Config:
        model_validate = True
