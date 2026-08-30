import json
from pathlib import Path
from typing import TypedDict, cast


class FileInfo(TypedDict):
    file_name: str
    file_hash: str


FilesMap = dict[str, FileInfo]


class ParseJson:
    path: Path

    def __init__(self, path_json: Path | str) -> None:
        self.path = Path(path_json)

    def read(self) -> FilesMap:
        with open(self.path, "r", encoding="utf-8") as f:
            return cast(FilesMap, json.load(f))

    def write(self, data: FilesMap):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
