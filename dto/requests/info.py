from typing import Optional
from pydantic import BaseModel, Field


class ServerInfoDTO(BaseModel):
    python_info: str = Field(min_length=1)


# DTO с информацией о клиенте
class ClientInfoDTO(BaseModel):
    client_ip: str
    useragent: str
    name_browser: Optional[str] = None


# DTO с информацией о БД
class DataBaseInfoDTO(BaseModel):
    database_name: str
    database_version: str
