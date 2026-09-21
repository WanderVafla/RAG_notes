# src/

## Responsibility
Application composition root + REPL entrypoint. Owns process startup (`src/main.py`) and delegates all orchestration to `src/agent/loop.run_agent`. No domain logic, parsing, or state lives here — only the interactive user loop.

## Design
Thin CLI loop, blocking `input()` REPL, no arg parsing, no DI container — direct import `run_agent`. Module layout: `agent/` (orchestration), `llm/` (client), `rag/` (retrieval), `tool/` (functions). `main.py` is 9 lines: single flat import, `if __name__ == "__main__"` guard, infinite `while True` with no exit command, exception handling, or logging configuration.

## Flow
`__main__` -> `while True: input("What is your ask? : ")` -> `run_agent(user_ask)` -> `print(response)`. Blocking synchronous cycle: each turn constructs a fresh `messages=[{'role':'user','content':user_input}]` inside `run_agent`, runs LLM tool-call loop to completion, returns final `message.content` for printing. Imports use flat `sys.path` style (`from agent.loop`, `from llm.client`) — implies `PYTHONPATH=src` or `src`-layout run (e.g. `python src/main.py` with `src` as cwd / `PYTHONPATH`).

## Integration
Entry `src/main.py` consumes `src/agent/loop.run_agent`. Runtime deps: qdrant via `docker-compose.yml` on `localhost:6333` (REST) / `6334` (gRPC), `python312` + `uv` via `flake.nix`, `.venv` activation, env `OPENROUTER_API_KEY` / `NOTES_FOLDER` / `LLM_MODEL`. `flake.nix` `shellHook` auto-creates `uv venv`, sources `.venv/bin/activate`, and runs `docker-compose up -d`; `agent/loop.py` loads env via `load_dotenv()` and instantiates `getClient()` at import time.
