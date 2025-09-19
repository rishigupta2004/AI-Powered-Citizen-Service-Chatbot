from .base_client import APIClient
from .schemas import AadhaarEKYC

class AadhaarClient(APIClient):
    def __init__(self, api_key: str | None = None):
        super().__init__("https://apisetu.gov.in/api/uidai", api_key)

    async def ekyc(self, aadhaar_no: str, otp: str) -> AadhaarEKYC:
        data = await self._get("ekyc_services", params={"aadhaar": aadhaar_no, "otp": otp})
        return AadhaarEKYC(**data)
