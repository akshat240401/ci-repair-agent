from __future__ import annotations
import hashlib
from pathlib import Path

TEXT_SUFFIXES = {".py", ".json", ".toml", ".yaml", ".yml", ".ini", ".cfg", ".txt"}

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def repo_state_hash(repo_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(repo_dir.rglob("*")):
        if not path.is_file():
            continue
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(repo_dir).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
