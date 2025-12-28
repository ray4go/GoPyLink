import functools

from gorayffi import cmds, ffi, handlers, registry
from gorayffi.actor import GolangLocalActor


class CrossLanguageClient:
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


@functools.lru_cache(maxsize=None)
def load_go_lib(libpath: str) -> CrossLanguageClient:
    cmder = ffi.load_go_lib(libpath, handlers.cmds_dispatcher(handlers.handlers))
    return CrossLanguageClient(cmder)


def export(func):
    """
    Register a python function/class to be called from go.

    Usage:
    @export
    def my_func(arg1, arg2):
        ...
    """
    registry.export_python(func)
    return func
