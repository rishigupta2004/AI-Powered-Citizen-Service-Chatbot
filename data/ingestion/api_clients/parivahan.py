from .base_client import APIClient
from .schemas import DLStatus

class ParivahanClient(APIClient):
    def __init__(self, api_key: str | None = None):
        super().__init__("https://apisetu.gov.in/api/parivahan", api_key)

    async def dl_status(self, dl_no: str, dob: str) -> DLStatus:
        data = await self._get("dl_status", params={"dl": dl_no, "dob": dob})
        return DLStatus(**data)
