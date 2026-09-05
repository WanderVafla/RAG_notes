import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openrouter import OpenRouter

from Core.VectoreStore import VectoreStore

_ = load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
NOTES_FOLDER = os.getenv("NOTES_FOLDER")
LLM_MODEL = os.getenv("LLM_MODEL")

if not api_key:
    sys.exit("Please set name of OPENROUTER_API_KEY in .env")
if not NOTES_FOLDER:
    sys.exit("Please set name of NOTES_FOLDER in .env")
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
    
notes_path = Path(NOTES_FOLDER)
if not notes_path.exists():
    raise FileNotFoundError(f"Folder with markdown notes not found on path {notes_path.resolve()}")

vectorStore = VectoreStore("markdown-notes")
vectorStore.sync_directory(path=Path(NOTES_FOLDER))

indexVectoreStore = VectorStoreIndex.from_vector_store(
    vector_store=vectorStore.getVectorStore()
)

collections = vectorStore.client.get_collections();
print("Существующие коллекции в Qdrant:", [c.name for c in collections.collections])

query_engine = indexVectoreStore.as_query_engine()
    
while True: 
    user_ask = input("What is your ask? : ");

    response = query_engine.query(user_ask)
    print(f"\n{response}")
    
    metadatas = response.metadata or {}
    sources = [meta['file_path'] for meta in metadatas.values() if meta.get('file_path')] or {}
    
    print(f"\nSources:\n\n{'\n'.join(s for s in sources or "Not found files")}\n")