from typing import List
from pydantic import BaseModel
from datetime import datetime


class UserResourceDTO(BaseModel):
    id: int
    username: str
    email: str
    birthday: str

    class Config:
        from_attributes = True
        model_validate = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def to_dict(self):
        return self.model_dump(mode="json")


class UsersResourceDTO(BaseModel):
    users: List[UserResourceDTO]

    class Config:
        from_attributes = True
        model_validate = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def to_dict(self):
        return self.model_dump(mode="json")


class UserFullResourceDTO(BaseModel):
    id: int
    username: str
    password: str
    email: str
    birthday: str

    class Config:
        from_attributes = True
        model_validate = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def to_dict(self):
        return self.model_dump(mode="json")