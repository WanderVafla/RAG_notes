# src/rag/

## Responsibility
Data Access / Retrieval Layer for RAG over markdown notes. Exposes single Facade `rag_search(query: str, limit: int)` for semantic retrieval over local `NOTES_FOLDER` of `.md` files. Hides Qdrant vector storage, ingestion/sync, embedding configuration, and `llama_index` retriever construction. No chat/prompt logic — pure retrieval of `NodeWithScore[]`.

Files:
- `__init__.py`: public export `rag_search`.
- `retriever.py`: `rag_search()` facade + module-level `init_settings()` side-effect on import.
- `VectorStore.py`: `VectorStore` wrapper over Qdrant + ingestion pipeline + docstore sync.
- `settings.py`: `init_settings()` global `llama_index.core.Settings` bootstrap.

## Design
- **Facade `rag_search`**: env check -> `VectorStore("markdown-notes")` -> `sync_directory()` -> `VectorStoreIndex.from_vector_store()` -> `as_retriever()` -> `retrieve(query)`.
- **Wrapper `VectorStore` over `QdrantVectorStore`**: encapsulates `qdrant_client.QdrantClient`, `QdrantVectorStore(collection_name=name)`, `StorageContext.from_defaults(vector_store=...)`.
- **IngestionPipeline with `MarkdownNodeParser` + `Settings.embed_model`**: `transformations=[MarkdownNodeParser(), Settings.embed_model]`, `docstore_strategy=DocstoreStrategy.UPSERTS`. Markdown-aware chunking + re-embedding, idempotent upserts.
- **DocstoreStrategy.UPSERTS + `SimpleDocumentStore` persisted to `{name}_docstore.json`**: local `markdown-notes_docstore.json` tracks `doc.id_` hashes; loaded via `_get_docstore()` (`from_persist_path` if exists else new), persisted after `pipeline.run()`.

Class `VectorStore` (`VectorStore.py:14-75`):
- Fields: `name: str`, `host="localhost"`, `port=6333`, `client: QdrantClient`, `vector_store: QdrantVectorStore`, `storage_context: StorageContext`, `docstore_path = f"{name}_docstore.json"`.
- `__init__(name, host, port)`: creates `QdrantClient(host, port)`, wraps in `QdrantVectorStore`, builds `StorageContext`.
- `getStorageContext() -> StorageContext`, `getVectorStore() -> QdrantVectorStore`.
- `_get_docstore() -> SimpleDocumentStore`: load-or-create.
- `sync_directory(path: Path)`: `SimpleDirectoryReader(input_dir=path, required_exts=[".md"], recursive=True).load_data()`; `doc.id_ = doc.metadata["file_path"]`; runs pipeline; persists docstore.

`init_settings()` (`settings.py:11-33`):
- `load_dotenv()`, reads `OPENROUTER_API_KEY`, `LLM_MODEL`, `sys.exit()` if missing.
- `Settings.llm = OpenRouter(model=LLM_MODEL)`.
- `Settings.embed_model = OpenAIEmbedding(model_name="baai/bge-m3", api_key=api_key, api_base="https://openrouter.ai/api/v1")` — used by pipeline and query-time embedding.

## Flow
`rag_search(query, limit)` (`retriever.py:13-33`):
1. Check `NOTES_FOLDER` env, `sys.exit()` if unset; `FileNotFoundError` if path missing.
2. `VectorStore("markdown-notes")`: connect Qdrant `localhost:6333`, collection `markdown-notes`.
3. `sync_directory(path)`: Reader `.md` recursive -> `doc.id_ = file_path` -> pipeline `run(documents)` -> `docstore.persist()`. Only new/changed embed + upsert.
4. `VectorStoreIndex.from_vector_store(vector_store=...)`: bind existing collection.
5. `as_retriever(similarity_top_k=limit)` -> `retrieve(query)`: embed query with `baai/bge-m3`, Qdrant cosine search, return `list[NodeWithScore]`.
6. `init_settings()` runs at `retriever.py:11` import time, so `from rag import rag_search` bootstraps `Settings` first.

## Integration
- Consumed by: `src/tool/registry.py` (`search_notes`, `find_and_read_file`).
- Depends on: `llama_index` (`Settings`, `SimpleDirectoryReader`, `StorageContext`, `VectorStoreIndex`, `IngestionPipeline`, `DocstoreStrategy`, `MarkdownNodeParser`, `SimpleDocumentStore`, `QdrantVectorStore`, `OpenAIEmbedding`, `OpenRouter`), `qdrant_client`, `python-dotenv`.
- Env: `OPENROUTER_API_KEY`, `LLM_MODEL`, `NOTES_FOLDER`.
- Infra: Docker Qdrant `localhost:6333`, collection `markdown-notes`, sidecar `markdown-notes_docstore.json` in CWD.
