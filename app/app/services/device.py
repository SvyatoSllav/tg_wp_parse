from app.repository.device import RepositoryDevice


class DeviceService:

    def __init__(
            self,
            repository_device: RepositoryDevice) -> None:
        self._repository_device = repository_device

    async def all_devices(self):
        return self._repository_device.list()

    async def get_device(self, device_id: str):
        return self._repository_device.get(device_id=device_id)

    async def create_device(self, data_in: int):
        return self._repository_device.create(
            obj_in=data_in, commit=True
        )

    async def delete_device(self, device_id: str):
        device = self._repository_device.get(device_id=device_id)
        self._repository_device.delete(db_obj=device)
