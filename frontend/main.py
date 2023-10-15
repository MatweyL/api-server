import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from server.adapters.outbound.s3_uploader.config import minio_uploader_config
from server.common.config import host_config


app = FastAPI()


templates = Jinja2Templates(directory="templates")


@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "minio_host": minio_uploader_config.host,
                                                     "server_url": host_config.server_url })


if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=80)
