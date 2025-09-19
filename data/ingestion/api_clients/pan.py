from .base_client import APIClient
from .schemas import PANVerification

class PANClient(APIClient):
    def __init__(self, api_key: str | None = None):
        super().__init__("https://apisetu.gov.in/api/pan", api_key)

    async def verify(self, pan: str) -> PANVerification:
        data = await self._get("verify", params={"pan": pan})
        return PANVerification(**data)
