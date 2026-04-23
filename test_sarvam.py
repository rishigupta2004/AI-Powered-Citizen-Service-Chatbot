import os
from sarvamai import SarvamAI
from dotenv import load_dotenv

load_dotenv()
client = SarvamAI()
print(client.text_to_speech.convert(
    inputs=["Hello world"],
    target_language_code="hi-IN",
    speaker="meera",
    pace=1.0,
    enable_preprocessing=True
))
