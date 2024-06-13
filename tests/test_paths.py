"""
Test paths.py.
"""

from pathlib import Path
from typing import List

import pytest

import tests
from doit_ext import paths


def test_find_python_source_files():
    """
    Test find_python_source_files.
    """
    result = paths.find_python_source_files(tests.SAMPLE_PROJECT_WITH_PYTHON_FILES)

    assert isinstance(result, list)
    assert tests.SAMPLE_PROJECT_SOME_FILE in result
    assert tests.SAMPLE_PROJECT_OTHER_FILE in result


@pytest.mark.parametrize(
    "path",
    [
        tests.SAMPLE_PROJECT_SOME_FILE,
        tests.SAMPLE_PROJECT_OTHER_FILE,
        tests.NON_EXISTING_PATH,
    ],
)
def test_hash_path_contents(path: Path):
    """
    Test hash_path_contents.
    """
    result = paths.hash_path_contents(path)
    assert isinstance(result, bytes)

    if path.exists():
        if len(path.read_bytes()) > 0:
            assert len(result) > 0
        else:
            assert len(result) == 0
    else:
        assert len(result) == 0


@pytest.mark.parametrize(
    "file_paths",
    tests.SAMPLE_PROJECT_FILE_PATHS,
)
def test_create_path_content_dict(file_paths: List[Path]):
    """
    Test create_path_content_dict.
    """
    result = paths.create_path_content_dict(file_paths=file_paths)
    assert isinstance(result, dict)


@pytest.mark.parametrize(
    "file_paths",
    tests.SAMPLE_PROJECT_FILE_PATHS,
)
def test_create_path_content_hash(file_paths: List[Path]):
    """
    Test create_path_content_hash.
    """
    assert isinstance(file_paths, list)
    assert all(isinstance(path, Path) for path in file_paths)
    result = paths.create_path_content_hash(file_paths=file_paths)
    assert isinstance(result, str)
