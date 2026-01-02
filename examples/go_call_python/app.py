import gopylink


@gopylink.export
def greet(name: str) -> str:
    return f"Hi, {name}!"


@gopylink.export
def multiply(a, b):
    return a * b


@gopylink.export
class Counter:
    def __init__(self, initial=0):
        self.value = initial

    def incr(self, n):
        self.value += n
        return self.value


lib = gopylink.load_go_lib("out/go.lib")
lib.func_call("Start")