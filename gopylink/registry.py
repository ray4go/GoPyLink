import inspect
from types import FunctionType


class PythonRegistry:
    _python_export_funcs: dict[str, FunctionType]
    _python_export_classes: dict[str, type]

    def __init__(self):
        self._python_export_funcs = {}
        self._python_export_classes = {}

    def export(self, cls_or_func):
        """
        Decorator to register a python function/class to be called from go.
        """
        if inspect.isfunction(cls_or_func):
            if cls_or_func.__name__ in self._python_export_funcs:
                raise ValueError(
                    f"Function {cls_or_func.__name__} is already exported."
                )
            self._python_export_funcs[cls_or_func.__name__] = cls_or_func
        elif inspect.isclass(cls_or_func):
            if cls_or_func.__name__ in self._python_export_classes:
                raise ValueError(f"Class {cls_or_func.__name__} is already exported.")
            self._python_export_classes[cls_or_func.__name__] = cls_or_func
        else:
            raise TypeError(f"Unknown type {type(cls_or_func)} to export.")
        return cls_or_func

    def get_export_python_func(self, func_name: str):
        """Internal use only."""
        return self._python_export_funcs.get(func_name)

    def get_export_python_class(self, cls_name: str):
        """Internal use only."""
        return self._python_export_classes.get(cls_name)
