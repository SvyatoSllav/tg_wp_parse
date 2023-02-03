from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.core.containers import Container
from app.api.deps import commit_and_close_session

from app.schemas.device import DeviceIn


router = APIRouter()


@router.get("/all_devices")
@inject
@commit_and_close_session
async def all_devices(device_service = Depends(Provide[Container.device_service])):
    return await device_service.all_devices()


@router.post("/create_device")
@inject
@commit_and_close_session
async def create_device(
        data_in: DeviceIn,
        device_service = Depends(Provide[Container.device_service])):
    return await device_service.create_device(data_in=data_in)


@router.delete("/delete_device")
@inject
@commit_and_close_session
async def delete_device(device_id: str, device_service = Depends(Provide[Container.device_service])):
    return await device_service.delete_device(device_id=device_id)
