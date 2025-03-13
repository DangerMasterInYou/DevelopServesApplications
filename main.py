import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
import json
import webbrowser

from sqlalchemy import select

from api.story.story import story
from database.connect import new_session
from fastapi.middleware.cors import CORSMiddleware
from api.info import info_router
from api.api_auth import api_auth_router
from api.db import db_router, setup_database, refresh_database
from api.api_ref.userAndRole import api_ref_user
from api.api_ref.policy.role import api_ref_policy_role
from api.api_ref.policy.permission import api_ref_policy_permission
import socket

from database.models.users import UserModel
from database.models.policy.permissions import PermissionModel
from database.models.policy.roles import RoleModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists("ServDevDB.db"):
        await setup_database()
    try:
        async with new_session() as session:
            result_user = (await session.execute(select(UserModel))).scalars().first()
            result_role = (await session.execute(select(RoleModel))).scalars().first()
            result_permission = (await session.execute(select(PermissionModel))).scalars().first()

            if (result_user is None
                    or result_role is None
                    or result_permission is None):
                await setup_database()
                await refresh_database(session)
    except Exception as e:
        raise
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"], )

app.include_router(info_router)
app.include_router(api_auth_router)
app.include_router(db_router)

prefix_api_ref = '/api/ref'
tags_api_ref = 'api_ref'
prefix_api_ref_policy = prefix_api_ref+'/policy'
tags_api_ref_policy = tags_api_ref+'_policy'
app.include_router(api_ref_user, prefix=prefix_api_ref, tags=[tags_api_ref])
app.include_router(api_ref_policy_role, prefix=prefix_api_ref_policy, tags=[tags_api_ref_policy])
app.include_router(api_ref_policy_permission, prefix=prefix_api_ref_policy,
                   tags=[tags_api_ref_policy])
app.include_router(story, prefix='/story', tags=['story'])


@app.get('/')
def hello():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    response = {"print": "Hello!", "ip_address": ip_address}
    return json.dumps(response)


if __name__ == '__main__':
    load_dotenv()
    host = os.getenv('HOST')
    site_port = int(os.getenv('SITE_PORT'))
    webbrowser.open(f'http://{host}:{site_port}/docs', new=2)
    uvicorn.run("main:app", host=host, port=site_port, log_level="info")
