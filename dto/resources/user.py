from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class UserResourceDTO(BaseModel):
    id: int
    username: str
    email: str
    birthday: str

    class Config:
        model_validate = True


class UsersResourceDTO(BaseModel):
    users: List[UserResourceDTO]

    class Config:
        model_validate = True
