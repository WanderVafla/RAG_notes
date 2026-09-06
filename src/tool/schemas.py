RAG_SEARCH_NOTES = {
    "type": "function",
    "function": {
        "name": "search_notes",
        "description": "Search the user's personal notes and study materials for content relevant to a topic or question. Use this whenever the user asks about something they might have written down, studied, or noted before.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "search query — can be a natural language question or topic, not just a single keyword",
                }
            },
            "required": ["query"],
        },
    },
}

TOOL_SCHEMAS = [RAG_SEARCH_NOTES]