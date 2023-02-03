from pathlib import Path

from app.api.api_v1 import api
from app.api.api_v1.endpoints import messengers, telegram, device, chat
from app.api import deps
from fastapi import FastAPI, Response
from app.core.config import settings
from app.core.containers import Container
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination


def create_app():
    container = Container()
    container.wire(modules=[deps, api, messengers, telegram, device, chat])
    fastapi_app = FastAPI(
        title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )
    fastapi_app.container = container

    current_file = Path(__file__)
    current_file_dir = current_file.parent
    project_root = current_file_dir.parent
    project_root_absolute = project_root.resolve()
    image_static_root_absolute = project_root_absolute / "image"
    fastapi_app.include_router(api.api_router, prefix=settings.API_V1_STR)
    fastapi_app.mount("/image", StaticFiles(directory=image_static_root_absolute), name="image")
    add_pagination(fastapi_app)
    return fastapi_app

app = create_app()
