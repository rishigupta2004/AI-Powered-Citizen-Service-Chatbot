from .base_client import APIClient
from .schemas import EPFOBalance

class EPFOClient(APIClient):
    def __init__(self, api_key: str | None = None):
        super().__init__("https://apisetu.gov.in/api/epfo", api_key)

    async def balance(self, uan: str) -> EPFOBalance:
        data = await self._get("balance", params={"uan": uan})
        return EPFOBalance(**data)
