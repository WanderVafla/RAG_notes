
import os

from dotenv.main import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv('OPENROUTER_API_KEY')
base_url = os.getenv('OPENROUTER_BASE_URL') or 'https://openrouter.ai/api/v1'

def getClient() -> OpenAI:
    if not api_key:
        raise RuntimeError("APIKeyValueError: Not found OpenAI api key")

    return OpenAI(
        base_url=base_url,
        api_key=api_key,
    )
