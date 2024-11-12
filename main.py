from fastapi import FastAPI
import uvicorn
import webbrowser
from api.info import info_router

app = FastAPI()

app.include_router(info_router)


@app.get('/')
def hello():
    return 1


if __name__ == '__main__':
    host = "127.0.0.1"
    port = 5000
    webbrowser.open(f'http://{host}:{port}/docs', new=2)
    uvicorn.run("main:app", host=host, port=port, log_level="info")
