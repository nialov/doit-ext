"""
Integration tests for doit-ext.
"""
from pathlib import Path
from subprocess import check_call
from textwrap import dedent

import pytest


def test_doit_ext_integration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """
    Test doit-ext functionality fully.
    """

    # TODO: Why does dedent not work with indented code here
    dodo_py_contents = dedent(
        f"""
from doit_ext.compose import ComposeTask
from pathlib import Path
def task_main():
    mkdir_cmd = "mkdir -p tmp"
    mkdir_cmd_2 = "mkdir -p tmp2"
    compose_task = (
        ComposeTask()
        .add_actions(mkdir_cmd)
        .add_config_dependency(dict(x=2))
        .add_config_dependency(dict(y=4))
        .add_file_deps(Path("setup.py"))
        .add_actions(mkdir_cmd_2)
    )
    return compose_task.compile()
            """.strip()
    )

    dodo_py_path = tmp_path / "dodo.py"

    setup_py_path = tmp_path / "setup.py"

    dodo_py_path.write_text(dodo_py_contents)
    setup_py_path.touch()

    monkeypatch.chdir(tmp_path)

    print(dodo_py_contents)

    check_call(["python", "-m", "doit", "list"])
    check_call(["python", "-m", "doit", "help"])
    check_call(["python", "-m", "doit"])

    tmp_path_tmp_dir = tmp_path / "tmp"
    tmp_path_tmp2_dir = tmp_path / "tmp2"

    for tmp_dir in (tmp_path_tmp_dir, tmp_path_tmp2_dir):
        assert tmp_dir.exists()
        assert tmp_dir.is_dir()
