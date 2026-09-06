import json
import os

from dotenv import load_dotenv

from llm.client import getClient
from tool.registry import TOOLS
from tool.schemas import TOOL_SCHEMAS

load_dotenv()
LLM_MODEL = os.getenv('LLM_MODEL')

client = getClient();

def execute_tool(name: str, arguments: dict) -> str:
    if name not in TOOLS:
        return f'Error: unknow tool "{name}"'
    try:
        return TOOLS[name](**arguments)
    except Exception as e:
        return f'ErrorRunTool: "{name}"'


def run_agent(user_input, verbose: bool = True):
    messages = [{'role': 'user', 'content': user_input}]
    
    while True:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
        )
        message = response.choices[0].message

        if message.tool_calls:
            messages.append(message.model_dump(exclude_unset=True))
            
            for tool_call in message.tool_calls:
                name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                if verbose:
                    print(f"\n`[tool call] {name}({arguments})`")
                    
                result = execute_tool(name, arguments)

                if verbose:
                    print(f"`[tool result] {result[:200]}\n`")


                messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call.id,
                    'content': result
                })

            continue
        return message.content