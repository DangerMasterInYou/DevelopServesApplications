from fastapi import FastAPI
from pydantic import BaseModel
import os
from typing import Optional
from fastapi.responses import HTMLResponse
import uvicorn




app = FastAPI()


@app.get('/')
def hello():
    html_content = "<h2>Hello World!</h2>"
    return HTMLResponse(content=html_content)

@app.get('/info/server')
def get_uvicorn_version():
    version = uvicorn.__version__
    html_content = f"<h2>uvicorn_version: {version}!</h2>"
    return HTMLResponse(content=html_content)


def dto():
    print("")


if __name__ == '__main__':
    dto()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
