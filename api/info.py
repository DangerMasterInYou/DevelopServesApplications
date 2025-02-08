from fastapi import APIRouter, Request
import platform
from dto.requests.info import ServerInfoDTO, ClientInfoDTO

info_router = APIRouter(prefix="/info", tags=["info"])


@info_router.get('/server')
def get_python_version():
    return ServerInfoDTO(python_info=platform.python_version())


@info_router.get('/client')
async def get_metadata_client(request: Request):
    client_ip = request.client.host
    useragent = request.headers.get("User-Agent")
    name_browser = "Vivaldi"
    return ClientInfoDTO(client_ip=client_ip, useragent=useragent, name_browser=name_browser)