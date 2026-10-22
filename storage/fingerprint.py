import hashlib
from pathlib import Path


def calculate_sha256(file_path: str | Path) -> str:
    """Calculate a file's SHA-256 fingerprint without loading it all into memory."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()