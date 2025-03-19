"""
Test compose.py.
"""

from contextlib import nullcontext as does_not_raise
from pathlib import Path

import pytest
from doit.task import Task, dict_to_task
from doit.tools import check_timestamp_unchanged, config_changed, result_dep

import tests
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
    "run_once",
    [True, False],
)
@pytest.mark.parametrize(
    "result_deps,config_changed",
    [
        (("hello_world", "hey_there"), None),
        (("hello_world", "hey_there"), dict(x=2, y="z")),
        (("hello_world", "hey_there"), dict(some_key=2, y="z")),
    ],
)
def test_uptodate(result_deps, config_changed, run_once):
    """
    Test UpToDate NamedTuple.
    """
    assert isinstance(result_deps, tuple)
    assert config_changed is None or isinstance(config_changed, dict)

    result = compose.UpToDate(
        result_deps=result_deps,
        config_changed=config_changed,
        run_once=False,
        extra_entries=(),
    )

    result_dep_additions = ("yes",)
    updated_result = result.update_result_deps(*result_dep_additions)
    assert updated_result.config_changed == config_changed

    assert all(
        addition in updated_result.result_deps for addition in result_dep_additions
    ), updated_result.result_deps

    config_changed_additions = dict(some_key=[1, 2, 3])

    config_updated_result = updated_result.update_config_changed(
        config_changed_additions
    ).update_run_once(run_once)

    assert config_updated_result.config_changed is not None
    for key, values in config_changed_additions.items():
        assert key in config_updated_result.config_changed
        assert config_updated_result.config_changed[key] == values

    assert config_updated_result.run_once == run_once


def test_composetask(data_regression):
    """
    Test ComposeTask.
    """

    mkdir_cmd = "mkdir -p tmp"
    mkdir_cmd_2 = "mkdir -p tmp2"
    setup_py_path = Path("setup.py")
    pyproject_toml_path = "pyproject.toml"
    target_csv_path = Path("target.csv")
    base_cmd = "python script.py {} {} {}"
    option_param = "--csv"
    new_name = "new_name"
    file_dep_param = compose.FileDep(pyproject_toml_path)
    target_param = compose.Target(target_csv_path)
    compose_task = (
        compose.ComposeTask(name="test_composetask_task")
        .add_actions(mkdir_cmd)
        .add_config_dependency(dict(x=2))
        .add_config_dependency(dict(y=4))
        .add_file_deps("dodo.py", setup_py_path)
        .add_result_dep("other_task")
        .add_actions(mkdir_cmd_2)
        .add_actions(
            compose.Action(
                base=base_cmd,
                parameters=(option_param, file_dep_param, target_param),
            )
        )
        .add_name(new_name)
        .add_actions(lambda: True)
        .toggle_run_once()
        .add_uptodate_entry(check_timestamp_unchanged("some_directory"))
    )

    assert compose_task.uptodate.config_changed is not None

    # Actions are not yet compiled so base_cmd should not yet be in config_changed
    assert base_cmd not in compose_task.uptodate.config_changed, compose_task
    assert base_cmd not in compose_task.uptodate.config_changed.values()

    compiled_compose_task = compose_task.compile()

    # Depends on order of result_dep and config_changed
    assert base_cmd in compiled_compose_task["uptodate"][-2].config

    assert isinstance(compiled_compose_task, dict)

    for key, values in compiled_compose_task.items():
        assert isinstance(key, str)

        assert isinstance(values, (tuple, str))

        if key == "actions":
            assert mkdir_cmd in values
            # Test that order is the same as inputted
            assert values.index(mkdir_cmd) < values.index(mkdir_cmd_2)
            assert base_cmd not in values
            assert (
                base_cmd.format(option_param, file_dep_param.value, target_param.value)
                in values
            )

        if key == "uptodate":
            # We expect these class instance to be in the values
            for expected_class in (
                config_changed,
                result_dep,
                check_timestamp_unchanged,
            ):
                assert any(isinstance(val, expected_class) for val in values)
            assert any("run_once" in str(val) for val in values)
            assert len(values) == 4
        if key == "name":
            assert isinstance(values, str)
            assert values == new_name

    # Test with doit task parsing to make sure the result is acceptable by doit
    assert isinstance(dict_to_task(compiled_compose_task), Task)

    # Test that duplicate targets are removed
    compose_task_with_duplicate_target = compose_task.add_targets(target_csv_path)
    compiled = compose_task_with_duplicate_target.compile()
    assert len(compiled["targets"]) == len(set(compiled["targets"]))

    # Regression test
    compiled_compose_task_regression = {
        key: tests.normalize_value_for_regression(value)
        for key, value in compiled_compose_task.items()
    }
    data_regression.check(compiled_compose_task_regression)


@pytest.mark.parametrize(
    "base,parameters,raises",
    [
        ("hello there {}!", ("Friend",), does_not_raise()),
        ("hello there {} {} {}!", ("Friend", "And", "Another"), does_not_raise()),
        ("hello there {}!", ("Friend", "Or", "Foe?"), pytest.raises(ValueError)),
        ("hello there!", ("Friend",), pytest.raises(ValueError)),
        ("hello there!", ("Friend", "Or", "Foe?"), pytest.raises(ValueError)),
    ],
)
def test_action(base, parameters: tuple, raises):
    """
    Test Action NamedTuple.
    """

    with raises:
        result = compose.Action(base=base, parameters=parameters).compile()
        assert isinstance(result, str)
        assert base[: base.index("{}")] in result
