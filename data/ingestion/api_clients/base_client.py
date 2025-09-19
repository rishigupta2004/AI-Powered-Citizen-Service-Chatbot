import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.app.config import APISETU_KEY

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom API error wrapper."""

class APIClient:
    def __init__(self, base_url: str, api_key: str | None = APISETU_KEY, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        await self.client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def _get(self, endpoint: str, params: dict = None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {"accept": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        try:
            resp = await self.client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"API error {resp.status_code}: {resp.text}")
            raise APIError(f"API call failed: {e}") from e
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
