import os
import sys

from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openrouter import OpenRouter
def init_settings(): 
    _ = load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL")
    
    if not api_key:
        sys.exit("Please set name of OPENROUTER_API_KEY in .env")
    if not LLM_MODEL:
        sys.exit("Please set name of LLM_MODEL in .env")
    
    try:
        llm = OpenRouter(
            model=LLM_MODEL,
        )
        Settings.llm = llm
        
        embed_model = OpenAIEmbedding(
            model_name="baai/bge-m3",
            api_key=api_key,
            api_base="https://openrouter.ai/api/v1",
        )
        Settings.embed_model = embed_model
    except Exception as e:
        sys.exit(f"InitModelsError: {e}")
    