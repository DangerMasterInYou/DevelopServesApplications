from typing import Optional
from pydantic import BaseModel, EmailStr


class AuthResourcesDTO(BaseModel):
    access_token: str
    refresh_token: Optional[str] = "0"
    user_id: int
    username: str
    email: EmailStr

    def __init__(
            self, access_token: str, user_id: int, username: str, email: EmailStr, refresh_token: Optional[str] = "0"):
        super().__init__(
            access_token=access_token, refresh_token=refresh_token, user_id=user_id, username=username, email=email
        )


class RegistrationResourcesDTO(BaseModel):
    user_id: int
    username: str
    email: EmailStr

    def __init__(self, user_id: int, username: str, email: EmailStr):
        super().__init__(user_id=user_id, username=username, email=email)
