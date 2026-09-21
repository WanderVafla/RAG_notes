# Repository Atlas: RAG_notes

## Project Responsibility
CLI RAG-агент по личным markdown-заметкам (Obsidian-style). Отвечает на вопросы пользователя через OpenAI function-calling loop: семантический поиск по Qdrant + файловые операции (`list`, `read`, `backlinks`, `recent`). Стек: Python 3.12 + `uv` (flake.nix), LlamaIndex (`MarkdownNodeParser`, `IngestionPipeline` UPSERTS, `baai/bge-m3` через OpenRouter), Qdrant в Docker, LLM через OpenAI-совместимый endpoint.

## System Entry Points
- `src/main.py`: REPL `while True: input("What is your ask? : ") -> run_agent() -> print()`. Composition root.
- `src/agent/loop.py`: `run_agent(user_input)` + `execute_tool(name, arguments)`. ReAct-цикл.
- `docker-compose.yml`: Qdrant `6333/6334`, volume `./qdrant_data`.
- `flake.nix`: `python312` + `uv` + `docker-compose`, `shellHook` авто-venv + `docker-compose up -d`.
- `.env.example`: `OPENROUTER_API_KEY`, `NOTES_FOLDER` (+ фактически `LLM_MODEL` из кода).

## Directory Map (Aggregated)
| Directory | Responsibility Summary | Detailed Map |
|-----------|------------------------|--------------|
| `src/` | Composition root + REPL entrypoint, thin CLI без DI/парсинга. | [View Map](src/codemap.md) |
| `src/agent/` | Orchestration Layer: ReAct function-calling loop, `messages` state, tool dispatch. | [View Map](src/agent/codemap.md) |
| `src/rag/` | Data Access / Retrieval: `rag_search` facade, Qdrant + IngestionPipeline, `init_settings`. | [View Map](src/rag/codemap.md) |
| `src/llm/` | Infrastructure adapter: `getClient() -> OpenAI` factory (сейчас `localhost:8080`). | [View Map](src/llm/codemap.md) |
| `src/tool/` | Tool layer: 6 note-операций + OpenAI schemas (`TOOLS`, `TOOL_SCHEMAS`). | [View Map](src/tool/codemap.md) |

## Cross-Cutting Flow
`main.py input -> agent/loop.run_agent -> llm/client.chat.completions.create(model=LLM_MODEL, tools=TOOL_SCHEMAS) -> tool/registry.TOOLS dispatch -> rag/retriever.rag_search -> VectorStore.sync_directory (Qdrant UPSERTS) -> retriever -> tool str -> agent tool-message -> LLM -> final answer`.
