"""
Tests for doit_ext.
"""

from pathlib import Path
from typing import Any, Callable, List

TESTS_PATH = Path(__file__).parent
SAMPLE_PROJECT_WITH_PYTHON_FILES = (
    TESTS_PATH / "sample_data/sample_project_with_python_files"
)

SAMPLE_PROJECT_SOME_FILE = SAMPLE_PROJECT_WITH_PYTHON_FILES / "some_file.py"
SAMPLE_PROJECT_OTHER_FILE = SAMPLE_PROJECT_WITH_PYTHON_FILES / "src/other_file.py"
NON_EXISTING_PATH = (
    SAMPLE_PROJECT_WITH_PYTHON_FILES / "src/other_file.py/and/so/on/some.py"
)

SAMPLE_PROJECT_FILE_PATHS = (
    [
        SAMPLE_PROJECT_SOME_FILE,
        SAMPLE_PROJECT_OTHER_FILE,
        NON_EXISTING_PATH,
    ],
)


def normalize_value_for_regression(value: Any):
    """
    Normalize doit dict values for regression testing.
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, tuple):
        new_value: List[str] = []
        for val in value:
            if isinstance(val, str):
                new_value.append(val)
            elif isinstance(val, Path):
                new_value.append(val.as_posix())
            elif callable(val):
                new_value.append(str(val.__class__))

            else:
                raise ValueError(f"Unhandled value of type: {type(val)}")
        return tuple(new_value)
    else:
        raise ValueError(f"Unhandled value of type: {type(value)}")
