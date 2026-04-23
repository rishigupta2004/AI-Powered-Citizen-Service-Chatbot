import os
from sarvamai import SarvamAI
from dotenv import load_dotenv

load_dotenv()
client = SarvamAI()
print(client.text_to_speech.convert(
    text="Hello world",
    model="bulbul:v3",
    target_language_code="hi-IN",
    speaker="meera",
    pace=1.0
))
