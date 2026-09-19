# src/agent/

## Responsibility
Orchestration Layer. Implements ReAct loop: interleaves LLM reasoning (`client.chat.completions.create`) with tool execution until final answer. Owns conversation state (`messages` list) and tool-call lifecycle. No tool implementations, no prompt construction, no LLM client construction.

## Design
- Pattern: OpenAI function-calling loop + Tool dispatch registry.
- Abstractions:
  - `LLM_MODEL: str` — loaded from env `LLM_MODEL` via `dotenv.load_dotenv()`. Passed as `model` on every completion call.
  - `client: OpenAI` — module singleton from `llm/client.getClient()`.
  - `TOOLS: dict[str, Callable]` — name -> function dispatch table from `tool/registry.py`.
  - `TOOL_SCHEMAS: list[dict]` — OpenAI `tools` specs from `tool/schemas.py`, passed verbatim to API.
- Interfaces:
  - `execute_tool(name: str, arguments: dict[str, Any]) -> str`: Guard `if name not in TOOLS` -> return `Error: unknow tool "{name}"`. Else `return TOOLS[name](**arguments)`. Blanket `except Exception` -> return `ErrorRunTool: "{name}"`. Always returns `str` for direct insertion as `tool` message content.
  - `run_agent(user_input: str, verbose: bool = True) -> str | None`: Initializes `messages = [{'role': 'user', 'content': user_input}]`, drives `while True` loop, returns `message.content` on terminal turn.

## Flow
1. `src/main.py` input -> `run_agent(user_input, verbose)`.
2. `run_agent` seeds `messages` with `{'role': 'user', 'content': user_input}`.
3. Loop: `client.chat.completions.create(model=LLM_MODEL, messages=messages, tools=TOOL_SCHEMAS)`.
4. Extract `message = response.choices[0].message`.
5. If `message.tool_calls` is truthy:
   - `messages.append(message.model_dump(exclude_unset=True))` — persists assistant turn with `tool_calls`.
   - For each `tool_call in message.tool_calls`: `name = tool_call.function.name`, `arguments = json.loads(tool_call.function.arguments)`. If `verbose`, print `[tool call]`.
   - `result = execute_tool(name, arguments)` -> `TOOLS[name](**arguments)`.
   - If `verbose`, print truncated `[tool result] {result[:200]}`.
   - `messages.append({'role': 'tool', 'tool_call_id': tool_call.id, 'content': result})`.
   - `continue` — next iteration re-queries LLM with extended history.
6. Else (no `tool_calls`): `return message.content`.

## Integration
- Consumed by: `src/main.py` (entrypoint, calls `run_agent`).
- Depends on:
  - `llm/client.getClient` -> `client` instance for `client.chat.completions.create`.
  - `tool/registry.TOOLS` -> runtime dispatch in `execute_tool`.
  - `tool/schemas.TOOL_SCHEMAS` -> `tools` parameter for function-calling.
  - Env: `LLM_MODEL` (required, defaults to `''` if unset).
