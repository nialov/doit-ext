"""
Compose doit tasks.
"""

from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from doit.tools import config_changed, result_dep, run_once

FuncType = Union[Callable, str]
StrPathType = Union[Path, str]


class FileDep(NamedTuple):
    """
    File dependency.
    """

    value: StrPathType


class Target(NamedTuple):
    """
    Target.
    """

    value: StrPathType


class Action(NamedTuple):
    """
    Action.
    """

    base: Union[str, Sequence[str]]
    parameters: Tuple[Union[FileDep, Target, Any], ...] = ()

    @property
    def base_str(self) -> str:
        """
        Get base as a joined string.
        """
        if isinstance(self.base, str):
            return self.base
        return str.join(" ", self.base)

    def validate(self):
        """
        Validate inputs.
        """
        if not self.base_str.count("{}") == len(self.parameters):
            raise ValueError(
                "Expected base to have {} format spots for every parameter."
            )

    def compile(self) -> str:
        """
        Compile into action string.
        """
        self.validate()
        if len(self.parameters) == 0:
            return self.base_str
        return self.base_str.format(
            *[
                param if not isinstance(param, (FileDep, Target)) else param.value
                for param in self.parameters
            ]
        )

    def file_deps(self) -> List[StrPathType]:
        """
        Get file dependencies.
        """
        file_deps = [
            param.value for param in self.parameters if isinstance(param, FileDep)
        ]
        return file_deps

    def targets(self) -> List[StrPathType]:
        """
        Get targets dependencies.
        """
        targets = [
            param.value for param in self.parameters if isinstance(param, Target)
        ]
        return targets

        # return (
        #     self.base
        #     else
        # )


ActionsType = Union[Action, FuncType]


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
    run_once: bool

    def update_result_deps(self, *result_deps: Any) -> "UpToDate":
        """
        Update result_deps values.
        """
        return UpToDate(
            result_deps=tuple([*self.result_deps, *result_deps]),
            config_changed=self.config_changed,
            run_once=self.run_once,
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
            run_once=self.run_once,
        )

    def update_run_once(self, value: bool) -> "UpToDate":
        """
        Update run_once addition.
        """
        return UpToDate(
            result_deps=self.result_deps,
            config_changed=self.config_changed,
            run_once=value,
        )

    def compile(self) -> Tuple[Any, ...]:
        """
        Compile UpToDate into doit uptodate values.
        """
        compiled = [result_dep(dep) for dep in self.result_deps]

        if self.run_once:
            compiled = [*compiled, run_once]

        if self.config_changed is not None:
            compiled = [*compiled, config_changed(self.config_changed)]
        return tuple(compiled)


class ComposeTask(NamedTuple):
    """
    Composeable task definition.
    """

    actions: Tuple[Union[FuncType, Action], ...] = ()
    file_dep: Tuple[StrPathType, ...] = ()
    task_dep: Tuple[FuncType, ...] = ()
    targets: Tuple[StrPathType, ...] = ()
    uptodate: UpToDate = UpToDate(result_deps=(), config_changed=None, run_once=False)
    name: Optional[str] = None

    def update(
        self,
        **update_values: Union[
            Tuple[
                Union[
                    FuncType,
                    StrPathType,
                    result_dep,
                ],
                ...,
            ],
            Dict[str, Any],
            str,
            ActionsType,
            bool,
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
            if key == "run_once":
                assert isinstance(new_values, bool)
                old_values_dict["uptodate"] = self.uptodate.update_run_once(new_values)
                continue
            # if key == "actions":
            #     assert isinstance(new_values, tuple)
            #     compiled_actions = []
            #     for action in new_values:
            #         if not isinstance(action, Action):
            #             compiled_actions.append(action)
            #         elif isinstance(action, Action):
            #             compiled_action = action.compile()
            #             if compiled_action not in compiled_actions:
            #                 compiled_actions.append(compiled_action)
            #             # file_deps = [
            #             #     param.value
            #             #     for param in action.parameters
            #             #     if isinstance(param, FileDep)
            #             # ]
            #             file_deps = action.file_deps()
            #             targets = action.targets()
            #             old_values_dict["file_dep"] = tuple(
            #                 [*old_values_dict["file_dep"], *file_deps]
            #             )
            #             old_values_dict["targets"] = tuple(
            #                 [*old_values_dict["targets"], *targets]
            #             )

            #             # Make task depend on the base action string
            #             old_values_dict["uptodate"] = (
            #                 self.uptodate.update_config_changed(
            #                     config={action.base: action.base}
            #                 )
            #             )
            #     old_values_dict[key] = tuple([*old_values_dict[key], *compiled_actions])
            #     continue

            if key not in old_values_dict:
                raise KeyError(f"Expected {key} to be a field of {self.__class__}.")

            attr = old_values_dict[key]
            if isinstance(attr, tuple):
                # Add values to current values
                old_values_dict[key] = tuple([*attr, *new_values])
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

    def add_actions(self, *actions: ActionsType) -> "ComposeTask":
        """
        Add actions to task.
        """
        return self.update(actions=actions)

    def add_file_deps(self, *file_deps: StrPathType) -> "ComposeTask":
        """
        Add file dependencies to task.
        """
        return self.update(file_dep=file_deps)

    def add_task_deps(self, *task_deps: FuncType) -> "ComposeTask":
        """
        Add task dependencies to task.
        """
        resolved_task_deps = (
            _resolve_task_dep(task_dep=task_dep) for task_dep in task_deps
        )

        return self.update(task_dep=tuple(resolved_task_deps))

    def add_targets(self, *targets: StrPathType) -> "ComposeTask":
        """
        Add targets to task.
        """
        return self.update(targets=targets)

    def add_result_dep(self, *result_deps: FuncType) -> "ComposeTask":
        """
        Add a result dependency.

        See: https://pydoit.org/uptodate.html#result-dependency
        """
        result_deps_called = (_resolve_task_dep(dep) for dep in result_deps)
        return self.update(result_deps=tuple(result_deps_called))

    def add_config_dependency(self, config_deps: Dict[str, Any]) -> "ComposeTask":
        """
        Add a config_changed dependency.

        See: https://pydoit.org/uptodate.html#config-changed
        """
        return self.update(config_changed=config_deps)

    def add_name(self, name: str) -> "ComposeTask":
        """
        Add a name overwriting any existing.
        """
        return self.update(name=name)

    def toggle_run_once(self) -> "ComposeTask":
        """
        Toggle run_once in uptodate config.
        """
        return self.update(run_once=not self.uptodate.run_once)

        # current_config_changed = (
        #     self.uptodate._config_changed.copy()
        #     if self.uptodate._config_changed is not None
        #     else {}
        # )
        # current_config_changed.update(config_deps)
        # return self.uptodate.update(dict(_config_changed=current_config_changed))

    def compile_actions(self) -> "ComposeTask":
        old_values_dict = _resolve_named_tuple_dict(self)
        old_values_dict.pop("actions")
        compiled_actions = []
        for action in self.actions:
            if not isinstance(action, Action):
                compiled_actions.append(action)
            else:
                compiled_action = action.compile()
                if compiled_action not in compiled_actions:
                    compiled_actions.append(compiled_action)
                file_deps = action.file_deps()
                targets = action.targets()
                old_values_dict["file_dep"] = tuple(
                    [*old_values_dict["file_dep"], *file_deps]
                )
                old_values_dict["targets"] = tuple(
                    [*old_values_dict["targets"], *targets]
                )

                # Make task depend on the base action string
                old_values_dict["uptodate"] = self.uptodate.update_config_changed(
                    config={action.base_str: action.base_str}
                )
        old_values_dict["actions"] = tuple(compiled_actions)
        return ComposeTask(**old_values_dict)

    def compile(self) -> Dict[str, Any]:
        """
        Compile into doit task dictionary definition.
        """
        actions_composed = self.compile_actions()
        resolved = _resolve_named_tuple_dict(actions_composed)
        resolved["uptodate"] = actions_composed.uptodate.compile()

        cleaned_resolved = resolved.copy()
        for key, items in resolved.items():
            # Remove dictionary keys with empty tuples as values
            if items is None or len(items) == 0:
                cleaned_resolved.pop(key)
            # Remove duplicate file deps and targets
            if key in ("file_deps", "targets"):
                cleaned_resolved[key] = tuple(set(items))

        return cleaned_resolved
