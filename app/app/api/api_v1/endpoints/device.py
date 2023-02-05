from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.core.containers import Container
from app.api.deps import commit_and_close_session

from app.schemas.device import DeviceIn, DeviceOut


router = APIRouter()


@router.get("/all_devices", response_model=list[DeviceOut])
@inject
@commit_and_close_session
async def all_devices(device_service = Depends(Provide[Container.device_service])):
    return await device_service.all_devices()


@router.get("/get_device", response_model=DeviceOut)
@inject
@commit_and_close_session
async def get_device(device_id: str, device_service = Depends(Provide[Container.device_service])):
    return await device_service.get_device(device_id=device_id)


@router.post("/create_device", response_model=DeviceOut)
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
