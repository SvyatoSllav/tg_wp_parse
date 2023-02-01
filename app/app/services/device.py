from app.repository.device import RepositoryDevice


class DeviceService:

    def __init__(
            self,
            repository_device: RepositoryDevice) -> None:
        self._repository_device = repository_device

    async def all_devices(self):
        return self._repository_device.list()

    async def create_device(self, data_in: int):
        return self._repository_device.create(
            obj_in=data_in, commit=True
        )
