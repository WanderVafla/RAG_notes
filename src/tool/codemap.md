# src/tool/

## Responsibility
Tool / Function-calling layer exposing note operations to LLM. Translates OpenAI `tool_call` objects into Python callables against `NOTES_FOLDER` vault and `rag.rag_search` retriever. All functions return `str` for direct LLM context injection. Files: `registry.py` (implementations + `TOOLS`), `schemas.py` (OpenAI function schemas + `TOOL_SCHEMAS`).

## Design
Registry pattern: `TOOLS: dict[str, Callable]` maps name -> impl. Declarative schemas: `TOOL_SCHEMAS: list[dict]` passed as `tools=` to chat API.

Tools (6) in `registry.py`:
1. `search_notes(query: str, limit: int = 5) -> str` — semantic search.
2. `find_and_read_file(query: str) -> str` — most-relevant full file.
3. `read_file(path: str) -> str` — exact path UTF-8 read.
4. `list_notes(folder: str = None) -> str` — enumerate `**/*.md`.
5. `find_backlinks(filename: str) -> str` — Obsidian wikilink reverse lookup.
6. `get_recent_notes(days: int = 7) -> str` — mtime-filtered listing.

Schema constants (6) in `schemas.py`, each `{"type": "function", "function": {"name", "description", "parameters"}}`:
1. `RAG_SEARCH_NOTES` (`search_notes`): `query: string`, `limit: integer [2,15]`; `required: ["query"]`.
2. `FIND_AND_READ_FILE`: `query: string`; `required: ["query"]`.
3. `LIST_NOTES`: `folder: string` optional; `required: []`.
4. `READ_FILE`: `path: string`; `required: ["path"]`.
5. `FIND_BACKLINKS`: `filename: string`; `required: ["filename"]`.
6. `GET_RECENT_NOTES`: `days: integer`; `required: []`.
Aggregate: `TOOL_SCHEMAS = [...]` (6 entries). `NOTES_FOLDER = os.getenv('NOTES_FOLDER') or ""` via `load_dotenv()` at import.

## Flow
`LLM tool_call -> agent execute_tool -> TOOLS[name](**arguments) -> str`:
1. `search_notes`: `rag_search(query, limit)` -> `str(response)`.
2. `find_and_read_file`: `rag_search(query, 10)` -> `"No relevant notes found."` if empty -> `Counter(file_path).most_common(1)` -> `read_file(most_common)`.
3. `read_file`: `Path(path)` -> `"This file not exist"` if missing -> `read_text(encoding='utf-8')`.
4. `list_notes`: `base = Path(NOTES_FOLDER)/folder or Path(NOTES_FOLDER)` -> `"Folder does not exist"` check -> `glob("**/*.md")` -> join or `"No notes found."`.
5. `find_backlinks`: `target = Path(filename).stem` -> `re.compile(r"\[\[stem(\|.*?)?\]\]")` -> scan `**/*.md` -> join or `"No backlinks found."`.
6. `get_recent_notes`: `cutoff = time.time() - days*86400` -> `mtime > cutoff` filter -> join or `"No recent notes."`.

## Integration
- Consumed by: `src/agent/loop.py` (`TOOLS`, `TOOL_SCHEMAS`).
- Depends on: `src/rag` (`from rag import rag_search`), env `NOTES_FOLDER`, stdlib `pathlib`, `re`, `time`, `collections.Counter`.
