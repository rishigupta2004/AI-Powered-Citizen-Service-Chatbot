from .base_client import APIClient
from .schemas import PassportKendra, PassportStatus

class PassportClient(APIClient):
    def __init__(self, api_key: str | None = None):
        super().__init__("https://apisetu.gov.in/api/passport", api_key)

    async def locate_psk(self, pin: str) -> dict:
        data = await self._get("locate_passport_seva_kendra", params={"pincode": pin})
        return [PassportKendra(**d) for d in data]

    async def track_status(self, file_no: str, dob: str) -> PassportStatus:
        data = await self._get("track_application_status", params={"fileNo": file_no, "dob": dob})
        return PassportStatus(**data)

# Alias to satisfy tests expecting this class name
class PassportAPIClient(PassportClient):
    pass
