import os
import sys
from pathlib import Path

from fsspec.spec import Any
from llama_index.core.indices.vector_store.base import VectorStoreIndex

from .VectorStore import VectorStore
from .settings import init_settings

init_settings()

def rag_search(query: str):
    NOTES_FOLDER = os.getenv("NOTES_FOLDER")
    if not NOTES_FOLDER:
        sys.exit("Please set name of NOTES_FOLDER in .env")

    notes_path = Path(NOTES_FOLDER)
    
    if not notes_path.exists():
        raise FileNotFoundError(f"Folder with markdown notes not found on path {notes_path.resolve()}")
    
    
    vectorStore = VectorStore("markdown-notes")
    vectorStore.sync_directory(path=notes_path)
    
    indexVectorStore = VectorStoreIndex.from_vector_store(
        vector_store=vectorStore.getVectorStore()
    )
        
    query_engine = indexVectorStore.as_query_engine()
    
    response = query_engine.query(query)
    return response, response.metadata