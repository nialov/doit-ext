"""
General utilities.
"""
from typing import Any


def command(*parts: Any) -> str:
    """
    Compile command-line command from parts.
    """
    return " ".join(list(map(str, parts)))
