# src/llm/

## Responsibility
LLM client factory / Infrastructure adapter. Sole file `client.py` exposing `getClient() -> OpenAI`. Isolates OpenAI-compatible client construction from agent logic. No prompt, model selection, or chat-loop logic.

## Design
Factory function over `openai.OpenAI`:
- `load_dotenv()` at import time.
- `getClient() -> OpenAI` reads `OPENROUTER_API_KEY`; raises `RuntimeError("APIKeyValueError: Not found OpenAI api key")` if falsy.
- Returns `OpenAI(base_url, api_key)` — OpenAI-compatible endpoint pattern, swappable without changing call sites.
- Discrepancy: active code hardcodes `base_url='http://localhost:8080/v1'` with `api_key="no-key-required"` (local inference server, e.g. llama.cpp / LM Studio). Intended production `base_url='https://openrouter.ai/api/v1'` + `api_key=api_key` is commented out. `OPENROUTER_API_KEY` check is currently dead code — validated but never passed through.

## Flow
1. `getClient()` -> `load_dotenv()` -> `os.getenv('OPENROUTER_API_KEY')`.
2. If missing -> `RuntimeError`.
3. Else `OpenAI(base_url='http://localhost:8080/v1', api_key="no-key-required")` returned.
4. Consumed at `src/agent/loop.py:13` import time: `client = getClient()`.
5. `run_agent()` calls `client.chat.completions.create(model=LLM_MODEL, messages=messages, tools=TOOL_SCHEMAS)`, appends `message.model_dump(exclude_unset=True)` + tool results, repeats until no `tool_calls`, returns `message.content`.

## Integration
- Consumed by: `src/agent/loop.py` (`from llm.client import getClient`). Singleton import-time instantiation.
- Depends on: `openai` (`OpenAI`), `python-dotenv`, env `OPENROUTER_API_KEY` (validated, unused due to hardcode).
- `LLM_MODEL` not consumed here; consumed in `loop.py` per-request as `model=LLM_MODEL`.
- Contrast `src/rag/settings.py`: uses `llama_index.llms.openrouter.OpenRouter(model=LLM_MODEL)` + `OpenAIEmbedding(baai/bge-m3, api_base="https://openrouter.ai/api/v1")` assigned to `Settings`; `sys.exit()` on missing keys vs `RuntimeError` here.
