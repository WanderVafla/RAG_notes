import os
from pathlib import Path

import qdrant_client
from llama_index.core import Settings, SimpleDirectoryReader
from llama_index.core.ingestion import DocstoreStrategy, IngestionPipeline
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client.qdrant_client import QdrantClient


class VectorStore:
    name: str
    host: str = "localhost"
    port: int = 6333
    client: QdrantClient
    vector_store: QdrantVectorStore
    storage_context: StorageContext

    def __init__(self, name: str, host: str = "localhost", port: int = 6333):
        self.path: Path | None = None
        
        self.name = name
        self.host = host
        self.port = port
        # Connect to Docker with Vector Database - Qdrant
        self.client = qdrant_client.QdrantClient(host=self.host, port=self.port)

        self.vector_store = QdrantVectorStore(
            client=self.client, collection_name=self.name
        )

        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
        self.docstore_path = f"{self.name}_docstore.json"

        

    def getStorageContext(self) -> StorageContext:
        return self.storage_context

    def getVectorStore(self) -> QdrantVectorStore:
        return self.vector_store

    def _get_docstore(self) -> SimpleDocumentStore:
            if os.path.exists(self.docstore_path):
                return SimpleDocumentStore.from_persist_path(self.docstore_path)
            return SimpleDocumentStore()
    
    def sync_directory(self, path: Path):
        documents = SimpleDirectoryReader(
            input_dir=path, required_exts=[".md"], recursive=True
        ).load_data()
    
        for doc in documents:
            doc.id_ = doc.metadata["file_path"]
    
        docstore = self._get_docstore()
    
        pipeline = IngestionPipeline(
            transformations=[
                MarkdownNodeParser(),
                Settings.embed_model
            ],
            vector_store=self.vector_store,
            docstore=docstore,
            docstore_strategy=DocstoreStrategy.UPSERTS,
        )
    
        pipeline.run(documents=documents)
            
        docstore.persist(self.docstore_path)