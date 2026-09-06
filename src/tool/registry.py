from rag import rag_search


def search_notes(query: str) -> str:
    response = rag_search(query)
    return str(response)
    
TOOLS = {
    'search_notes': search_notes
}