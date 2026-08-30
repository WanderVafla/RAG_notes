import hashlib


def getHashFile(path: str) -> str:
    with open(path, 'rb') as file:
        return hashlib.sha256(file.read()).hexdigest()