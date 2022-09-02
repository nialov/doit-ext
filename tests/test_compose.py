"""
Test compose.py.
"""
from pathlib import Path

import pytest
from doit.tools import config_changed, result_dep

from doit_ext import compose


def task_hey_there():
    """
    Dummy task.
    """


@pytest.mark.parametrize(
    "task_dep",
    [
        "task_hello_world",
        task_hey_there,
    ],
)
def test__resolve_task_dep(task_dep):
    """
    Test _resolve_task_dep.
    """
    result = compose._resolve_task_dep(task_dep=task_dep)
    assert isinstance(result, str)


@pytest.mark.parametrize(
    "result_deps,config_changed",
    [
        (("hello_world", "hey_there"), None),
        (("hello_world", "hey_there"), dict(x=2, y="z")),
        (("hello_world", "hey_there"), dict(some_key=2, y="z")),
    ],
)
def test_uptodate(result_deps, config_changed):
    """
    Test UpToDate NamedTuple.
    """
    assert isinstance(result_deps, tuple)
    assert config_changed is None or isinstance(config_changed, dict)

    result = compose.UpToDate(result_deps=result_deps, config_changed=config_changed)

    result_dep_additions = ("yes",)
    updated_result = result.update_result_deps(*result_dep_additions)
    assert updated_result.config_changed == config_changed

    assert all(
        addition in updated_result.result_deps for addition in result_dep_additions
    ), updated_result.result_deps

    config_changed_additions = dict(some_key=[1, 2, 3])

    config_updated_result = updated_result.update_config_changed(
        config_changed_additions
    )

    assert config_updated_result.config_changed is not None
    for key, values in config_changed_additions.items():
        assert key in config_updated_result.config_changed
        assert config_updated_result.config_changed[key] == values


def test_composetask():
    """
    Test ComposeTask.
    """

    mkdir_cmd = "mkdir -p tmp"
    compose_task = (
        compose.ComposeTask()
        .add_actions(mkdir_cmd)
        .add_config_dependency(dict(x=2))
        .add_config_dependency(dict(y=4))
        .add_file_deps("dodo.py", Path("setup.py"))
        .add_result_dep("other_task")
    )

    compiled_compose_task = compose_task.compile()

    assert isinstance(compiled_compose_task, dict)

    for key, values in compiled_compose_task.items():
        assert isinstance(key, str)

        assert isinstance(values, (tuple, str))

        if key == "actions":
            assert mkdir_cmd in values

        if key == "uptodate":
            assert all(isinstance(val, (config_changed, result_dep)) for val in values)
