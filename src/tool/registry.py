import os
import re
import time
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

from rag import rag_search

load_dotenv()
NOTES_FOLDER = os.getenv("NOTES_FOLDER") or ""


def search_notes(query: str, limit: int = 5) -> str:
    response = rag_search(query, limit)

    return str(response)


def read_file(path: str | Path) -> str:
    path = Path(path)

    if not path.exists():
        return f"This file not exist {path}"

    return path.read_text(encoding="utf-8")


def find_and_read_file(query: str) -> str:
    response = rag_search(query, 10)

    if not response:
        return "No relevant notes found."

    file_paths = [
        n.metadata.get("file_path") for n in response if n.metadata.get("file_path")
    ]
    most_common_file: str | None = (
        Counter(file_paths).most_common(1)[0][0] or file_paths[0]
    )

    return read_file(most_common_file or "No corresponding file found")


def list_notes(folder: str | None = None) -> str:
    base = Path(NOTES_FOLDER) / folder if folder else Path(NOTES_FOLDER)

    if not base.exists():
        return f"Folder does not exist: {base}"

    files = list(base.glob("**/*.md"))
    return "\n".join(str(f) for f in files) or "No notes found."


def find_backlinks(filename: str) -> str:
    target = Path(filename).stem  # имя файла без расширения и пути
    pattern = re.compile(rf"\[\[{re.escape(target)}(\|.*?)?\]\]")

    matches = []
    for md_file in Path(NOTES_FOLDER).glob("**/*.md"):
        content = md_file.read_text(encoding="utf-8")
        if pattern.search(content):
            matches.append(str(md_file))

    return "\n".join(matches) or "No backlinks found."


def get_recent_notes(days: int = 7) -> str:
    cutoff = time.time() - (days * 86400)

    recent = [
        str(f) for f in Path(NOTES_FOLDER).glob("**/*.md") if f.stat().st_mtime > cutoff
    ]
    return "\n".join(recent) or "No recent notes."


TOOLS = {
    "search_notes": search_notes,
    "find_and_read_file": find_and_read_file,
    "read_file": read_file,
    "list_notes": list_notes,
    "find_backlinks": find_backlinks,
    "get_recent_notes": get_recent_notes,
}
