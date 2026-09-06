
import os

from dotenv.main import load_dotenv
from openai import OpenAI

load_dotenv()

def getClient() -> OpenAI:
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise RuntimeError("APIKeyValueError: Not found OpenAI api key")

    return OpenAI(
        base_url='https://openrouter.ai/api/v1',
        api_key=api_key,
    )