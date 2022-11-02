"""
General utilities.
"""
from typing import Any, Tuple


def command(*parts: Tuple[Any]) -> str:
    """
    Compile command-line command from parts.
    """
    return " ".join(list(map(str, parts)))
