from fastapi import APIRouter, Request
import platform
from database import engine
from sqlalchemy import text

from models.info import ServerInfoDTO, ClientInfoDTO, DataBaseInfoDTO

info_router = APIRouter(prefix="/info", tags=["info"])


@info_router.get('/server')
def get_python_version():
    return ServerInfoDTO(python_info=platform.python_version())


@info_router.get('/client')
async def get_metadata_client(request: Request):
    client_ip = request.client.host
    useragent = request.headers.get("User-Agent")
    return ClientInfoDTO(client_ip=client_ip, useragent=useragent)


@info_router.get('/database')
def get_info_database():
    database_name = engine.url.database
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version()"))
        database_version = result.fetchone()[0]
    return DataBaseInfoDTO(database_name=database_name, database_version=database_version)