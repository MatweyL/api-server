from fastapi import APIRouter

from service.domain.main import router_tasks

router_v1 = APIRouter(prefix="/v1", tags=["API version 1"])


@router_v1.get('/ping')
async def ping_api():
    return {'ping': 'pong'}

router_v1.include_router(router_tasks)
