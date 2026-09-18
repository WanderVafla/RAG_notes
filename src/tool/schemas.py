from array import array


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
                },
                "limit": {
                    "type": "integer",
                    "description": "maximum number of note excerpts to retrieve, default is 5. Increase for broad or multi-part questions, decrease for narrow, specific questions.",
                    "minimum": 2,
                    "maximum": 15
                }
            },
            "required": ["query"],
        },
    },
}

FIND_AND_READ_FILE = {
    "type": "function",
    "function": {
        "name": "find_and_read_file",
        "description": "Find the single note file most relevant to a topic and return its full content. Use this when the user wants to read an entire note, not just a snippet — e.g. 'read my notes on X', 'show me the full note about Y'.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "topic or question describing which note file to find",
                }
            },
            "required": ["query"],
        },
    },
}

LIST_NOTES = {
    "type": "function",
    "function": {
        "name": "list_notes",
        "description": "List all note filenames, optionally filtered to a specific folder. Use this when the user wants an overview of what notes exist, not a search for specific content.",
        "parameters": {
            "type": "object",
            "properties": {
                "folder": {
                    "type": "string",
                    "description": "optional folder name to filter by, e.g. 'Algorithms'. Omit to list all notes.",
                }
            },
            "required": [],
        },
    },
}

READ_FILE = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the full content of a specific note file when you already know its exact path (e.g. from a previous search_notes or list_notes result).",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "the full file path of the note to read",
                }
            },
            "required": ["path"],
        },
    },
}

FIND_BACKLINKS = {
    "type": "function",
    "function": {
        "name": "find_backlinks",
        "description": "Find all notes that link to a given note via an Obsidian [[wikilink]]. Use this to explore how a topic connects to other notes.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "the filename (with or without path/extension) of the note to find backlinks for",
                }
            },
            "required": ["filename"],
        },
    },
}

GET_RECENT_NOTES = {
    "type": "function",
    "function": {
        "name": "get_recent_notes",
        "description": "List notes modified within the last N days. Use this for questions about recent work or activity, e.g. 'what have I worked on lately'.",
        "parameters": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "number of days to look back, default is 7",
                }
            },
            "required": [],
        },
    },
}

TOOL_SCHEMAS = [RAG_SEARCH_NOTES, FIND_AND_READ_FILE, LIST_NOTES, READ_FILE, FIND_BACKLINKS, GET_RECENT_NOTES]