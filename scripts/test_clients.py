import asyncio
import os
from dotenv import load_dotenv
from data.ingestion.api_clients.passport import PassportClient
from data.ingestion.api_clients.aadhaar import AadhaarClient
from data.ingestion.api_clients.epfo import EPFOClient
from data.ingestion.api_clients.pan import PANClient
from data.ingestion.api_clients.parivahan import ParivahanClient

load_dotenv()
API_KEY = os.getenv("APISETU_KEY")

async def main():
    if not API_KEY:
        print("⚠️ No APISETU_KEY in .env, skipping live tests.")
        return

    passport = PassportClient(API_KEY)
    aadhaar = AadhaarClient(API_KEY)
    epfo = EPFOClient(API_KEY)
    pan = PANClient(API_KEY)
    parivahan = ParivahanClient(API_KEY)

    # Replace params with real values once you have them
    try:
        res = await passport.locate_psk("110001")
        print("Passport PSK:", res)
    except Exception as e:
        print("Passport error:", e)

    await passport.close()
    await aadhaar.close()
    await epfo.close()
    await pan.close()
    await parivahan.close()

if __name__ == "__main__":
    asyncio.run(main())
