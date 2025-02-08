import os
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
import json
import webbrowser
from fastapi.middleware.cors import CORSMiddleware
from api.info import info_router
from api.api_auth import api_auth_router
from api.db import db_router
import socket

app = FastAPI()

# Укажите допустимые источники
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"], )

app.include_router(info_router)
app.include_router(api_auth_router)
app.include_router(db_router)


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
