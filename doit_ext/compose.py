"""
Compose doit tasks.
"""

from pathlib import Path
from typing import Any, Callable, Dict, NamedTuple, Optional, Tuple, Union

from doit.tools import config_changed, result_dep

FuncType = Union[Callable, str]
StrPathType = Union[Path, str]


def _resolve_task_dep(task_dep: FuncType) -> str:
    """
    Resolve task dependency to doit task name.
    """
    prefix = "task_"
    task_dep_str = task_dep if isinstance(task_dep, str) else task_dep.__name__
    if task_dep_str.startswith(prefix):
        return task_dep_str.replace(prefix, "")
    return task_dep_str


def _resolve_named_tuple_dict(named_tuple: NamedTuple):
    """
    Resolve self into dict.
    """
    return {field: getattr(named_tuple, field) for field in named_tuple._fields}


class UpToDate(NamedTuple):
    """
    Class for uptodate spec.
    """

    result_deps: Tuple[str, ...]
    config_changed: Optional[Dict[str, Any]]

    def update_result_deps(self, *result_deps: Any) -> "UpToDate":
        """
        Update result_deps values.
        """
        return UpToDate(
            result_deps=tuple([*self.result_deps, *result_deps]),
            config_changed=self.config_changed,
        )

    def update_config_changed(self, config: Dict[str, Any]) -> "UpToDate":
        """
        Update config_changed values.
        """
        if self.config_changed is None:
            updated_config_changed = config
        else:
            updated_config_changed = self.config_changed.copy()
            updated_config_changed.update(config)
        return UpToDate(
            result_deps=self.result_deps,
            config_changed=updated_config_changed,
        )

    def compile(self) -> Tuple[Any, ...]:
        """
        Compile UpToDate into doit uptodate values.
        """
        called_result_deps = tuple(result_dep(dep) for dep in self.result_deps)
        if self.config_changed is None:
            return called_result_deps
        return tuple([config_changed(self.config_changed), *called_result_deps])


class ComposeTask(NamedTuple):
    """
    Composeable task definition.
    """

    actions: Tuple[FuncType, ...] = ()
    file_dep: Tuple[StrPathType, ...] = ()
    task_dep: Tuple[FuncType, ...] = ()
    targets: Tuple[StrPathType, ...] = ()
    uptodate: UpToDate = UpToDate(result_deps=(), config_changed=None)
    name: Optional[str] = None

    def update(
        self,
        update_values: Dict[
            str,
            Union[
                Tuple[
                    Union[
                        FuncType,
                        StrPathType,
                        result_dep,
                    ],
                    ...,
                ],
                Dict[str, Any],
            ],
        ],
    ) -> "ComposeTask":
        """
        Update values.
        """
        old_values_dict = _resolve_named_tuple_dict(self)
        for key, new_values in update_values.items():

            if key == "config_changed":
                assert isinstance(new_values, dict)
                old_values_dict["uptodate"] = self.uptodate.update_config_changed(
                    new_values
                )
                continue

            if key == "result_deps":
                assert isinstance(new_values, tuple)
                old_values_dict["uptodate"] = self.uptodate.update_result_deps(
                    *new_values
                )
                continue
            if key not in old_values_dict:
                raise KeyError(f"Expected {key} to be a field of {self.__class__}.")

            attr = old_values_dict[key]
            if isinstance(attr, Tuple):
                # Add values to current values
                old_values_dict[key] = tuple([*old_values_dict[key], *new_values])
            elif isinstance(attr, str):
                # Overwrite current value
                old_values_dict[key] = new_values
            elif attr is None:
                if key == "name":
                    assert isinstance(new_values, str)
                    old_values_dict[key] = new_values
            else:
                raise TypeError(f"Unexpected attr type: {type(attr)}.")
        return ComposeTask(**old_values_dict)

    def add_actions(self, *actions: FuncType) -> "ComposeTask":
        """
        Add actions to task.
        """
        return self.update(dict(actions=actions))

    def add_file_deps(self, *file_deps: StrPathType) -> "ComposeTask":
        """
        Add file dependencies to task.
        """
        return self.update(dict(file_dep=file_deps))

    def add_task_deps(self, *task_deps: FuncType) -> "ComposeTask":
        """
        Add task dependencies to task.
        """
        resolved_task_deps = (
            _resolve_task_dep(task_dep=task_dep) for task_dep in task_deps
        )

        return self.update(dict(task_dep=tuple(resolved_task_deps)))

    def add_targets(self, *targets: StrPathType) -> "ComposeTask":
        """
        Add targets to task.
        """
        return self.update(dict(targets=targets))

    def add_result_dep(self, *result_deps: FuncType) -> "ComposeTask":
        """
        Add a result dependency.

        See: https://pydoit.org/uptodate.html#result-dependency
        """
        result_deps_called = (_resolve_task_dep(dep) for dep in result_deps)
        return self.update(dict(result_deps=tuple(result_deps_called)))

    def add_config_dependency(self, config_deps: Dict[str, Any]) -> "ComposeTask":
        """
        Add a config_changed dependency.

        See: https://pydoit.org/uptodate.html#config-changed
        """
        return self.update(dict(config_changed=config_deps))

        # current_config_changed = (
        #     self.uptodate._config_changed.copy()
        #     if self.uptodate._config_changed is not None
        #     else {}
        # )
        # current_config_changed.update(config_deps)
        # return self.uptodate.update(dict(_config_changed=current_config_changed))

    def compile(self) -> Dict[str, Any]:
        """
        Compile into doit task dictionary definition.
        """
        resolved = _resolve_named_tuple_dict(self)
        resolved["uptodate"] = self.uptodate.compile()

        # Remove dictionary keys with empty tuples as values
        cleaned_resolved = resolved.copy()
        for key, items in resolved.items():
            if items is None or len(items) == 0:
                cleaned_resolved.pop(key)

        return cleaned_resolved
