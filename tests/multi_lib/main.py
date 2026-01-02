import pytest

import gopylink
from gopylink import registry

exports = registry.PythonRegistry()


@gopylink.export
def add(a, b):
    return a + b


@gopylink.export
@exports.export
def hello(name):
    return "hello " + name


@exports.export
class Counter:
    def __init__(self, initial=0):
        self.value = initial

    def incr(self, n=1):
        self.value += n
        return self.value

    def value(self):
        return self.value


lib_a = gopylink.load_go_lib("out/a.lib")
lib_b = gopylink.load_go_lib("out/b.lib")
lib_c = gopylink.load_go_lib("out/c.lib", exports)

#### a

m, n = lib_a.func_call("Divide", 10, 3)
assert m == 3 and n == 1

res = lib_a.func_call("NoReturnVal", 1, 2)
assert res is None

res = lib_a.func_call("Add2Points", {"X": 1, "Y": 2}, {"X": 3, "Y": 4})
assert res == {"X": 4, "Y": 6}

res = lib_a.func_call("CallPy", "hello", "world")
assert res == "hello world"

res = lib_a.func_call("CallPy", "add", 1, 2)
assert res == 3

#### b

counter = lib_b.new_type("Counter", 1)
assert counter.Incr(10) == 11
assert counter.Incr(1) == 12

res = lib_b.func_call("CallPy", "hello", "world")
assert res == "hello world"

res = lib_b.func_call("CallPy", "add", 1, 2)
assert res == 3

with pytest.raises(Exception):
    lib_c.func_call("CallPy", "add", 1, 2)

#### c

res = lib_c.func_call("CallPy", "hello", "world")
assert res == "hello world"

with pytest.raises(Exception):
    lib_c.func_call("CallPy", "add", 1, 2)

obj = lib_c.new_type("NewPyObj", "Counter", 1)
assert obj.MethodCall("incr", 10) == 11
