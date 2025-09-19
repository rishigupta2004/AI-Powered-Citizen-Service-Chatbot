import os
from dotenv import load_dotenv

load_dotenv()

APISETU_KEY = os.getenv("APISETU_KEY", "")
