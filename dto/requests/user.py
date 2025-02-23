from pydantic import BaseModel, EmailStr
from typing import Optional

from database.models.users import UserModel


class CreateUserRequestDTO(BaseModel):
    username: str
    password: str
    email: EmailStr
    birthday: str

    def to_dto(self) -> UserModel:
        return UserModel(
            username=self.username,
            password=self.password,
            email=self.email,
            birthday=self.birthday
        )


class UpdateUserRequestDTO(BaseModel):
    username: Optional[str]
    password: Optional[str]
    email: Optional[EmailStr]
    birthday: Optional[str]

    def apply_to_model(self, user_model: UserModel, updated_by: int):
        user_model.username = self.username if self.username is not None else user_model.username
        user_model.password = self.password if self.password is not None else user_model.password
        user_model.email = self.email if self.email is not None else user_model.email
        user_model.birthday = self.birthday if self.birthday is not None else user_model.birthday

