import asyncio
from data.ingestion.api_clients.passport import PassportClient

async def main():
    api_key = "YOUR_APISETU_KEY"  # load from .env later
    client = PassportClient(api_key)
    try:
        res = await client.locate_psk("110001")
        print("PSK Result:", res)
    except Exception as e:
        print("Error:", e)
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
