from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .router_v1 import router_v1

origins = ["*"]

SERVICE_TITLE = "Image Generator Service API"
SERVICE_DESCRIPTION = """Image generating by text description"""


def create_application() -> FastAPI:
    app = FastAPI(title=SERVICE_TITLE, description=SERVICE_DESCRIPTION)
    app.include_router(router_v1)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
