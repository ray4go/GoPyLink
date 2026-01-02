from __future__ import annotations

import functools
from typing import Optional

import gorayffi
from gorayffi import cmds, handlers
from gorayffi.actor import GolangLocalActor

from . import registry as registry_module

global_registry = registry_module.PythonRegistry()


@functools.lru_cache(maxsize=None)
def load_go_lib(
    libpath: str,
    python_registry: Optional[registry_module.PythonRegistry] = None,
) -> GolangClient:
    """
    Load a golang shared library, export python functions/classes to golang.
    Return the golang handler, which you can call golang functions/types defined in it.

    :param libpath: The path to the go shared library.
    :param python_registry: The registry to use for exporting python functions/classes.
    :return:
    """
    python_registry = python_registry or global_registry
    cmder = gorayffi.load_go_lib(
        libpath,
        handlers.get_handlers(
            python_registry.get_export_python_func,
            python_registry.get_export_python_class,
        ),
    )
    return GolangClient(cmder)


def export(func):
    """
    Decorator to register a python function/class to be called from go.

    Usage:
    @export
    def my_func(arg1, arg2):
        ...
    """
    global_registry.export(func)
    return func


class GolangClient:
    def __init__(self, cmder: cmds.GoCommander):
        self._cmder = cmder

    def func_call(self, func_name: str, *args):
        """
        Call a golang function.

        :param func_name: The name of the golang function to call.
        :param args: The arguments to pass to the golang function, only optional arguments are supported.
        :return: The return value of the golang function.
        """
        return self._cmder.call_golang_func(func_name, args)

    def new_type(self, type_name: str, *args) -> GolangLocalActor:
        """
        Create a new golang type.

        :param type_name: The name of the golang actor type to create.
        :param args: The arguments to pass to the golang type constructor.
        :return: The golang type instance.
        """
        return GolangLocalActor(self._cmder, type_name, *args)
