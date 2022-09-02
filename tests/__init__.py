"""
Tests for doit_ext.
"""

from pathlib import Path

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
