"""
Path utilities.
"""

from hashlib import md5
from pathlib import Path
from pickle import dumps
from typing import Dict, List


def find_python_source_files(base_dir: Path) -> List[Path]:
    """
    Find python (.py) source files in base_dir.
    """
    return list(base_dir.rglob("*.py"))


def create_path_content_dict(file_paths: List[Path]) -> Dict[str, bytes]:
    """
    Create hash from paths including their possible contents.
    """
    path_content_dict = {str(path): hash_path_contents(path) for path in file_paths}
    return path_content_dict


def hash_path_contents(path: Path) -> bytes:
    """
    Create hash of file contents at path if it exists.
    """
    if not path.exists():
        return b""
    contents = path.read_bytes()
    if len(contents) == 0:
        return b""
    hashed = md5(contents, usedforsecurity=False).digest()
    return hashed


def create_path_content_hash(file_paths: List[Path]) -> str:
    """
    Create doit usable hash from file_paths.
    """
    hashed = create_path_content_dict(file_paths=file_paths)
    hashed_json = dumps(hashed)
    return md5(hashed_json, usedforsecurity=False).hexdigest()
