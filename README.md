# GoPyLink

A lightweight Python & Go cross-language call framework for in-process communication.

## Features

- **Python Call Go** - Python call Go functions, create Go type instances and invoke methods
- **Go Call Python** - Go call Python functions, create Python class instances and invoke methods
- **Simple API** - Minimal setup with intuitive interfaces

## Limitations

GoPyLink is designed for **data exchange only**. All function parameters and return values must be plain data types (primitives, collections, structs with all fields public).

Channels, goroutines, functions and interface types (except `any`) are not supported as parameters or return values.


## Installation

**Go**

```bash
go get github.com/ray4go/go-ray/gopylink
```

**Python**

```bash
pip install gopylink
```

Requires: Go 1.21+, Python 3.7+

<details>
  <summary>C build environment is required, click to show installation commands. </summary>

```bash
# Ubuntu/Debian
sudo apt install build-essential

# CentOS/RHEL
sudo yum groupinstall "Development Tools"

# macOS
xcode-select --install
```
</details>

## Python calling Go

### 1. Export Go Functions/Types

Create a `lib.go` file:

```go
package main

import "github.com/ray4go/gopylink"

// Functions to export - all exported methods become callable from Python
type Functions struct{}

func (Functions) Hello(name string) string {
	return "Hello " + name
}

func (Functions) Add(a, b int) int {
	return a + b
}

// Classes to export - each method creates a new instance
type Classes struct{}

type Counter struct {
	value int
}

func (Classes) Counter(initial int) *Counter {
	return &Counter{value: initial}
}

func (c *Counter) Incr(n int) int {
	c.value += n
	return c.value
}

func (c *Counter) Value() int {
	return c.value
}

func init() {
	gopylink.Init(Functions{}, Classes{})
}

func main() {}
```

### 2. Build Go Shared Library

```bash
go build -buildmode=c-shared -o go.lib .
```

### 3. Call Go from Python

```python
# main.py
import gopylink

# Load the Go library
lib = gopylink.load_go_lib("go.lib")

# Call Go functions
result = lib.func_call("Hello", "World")
print(result)  # Output: Hello World

result = lib.func_call("Add", 10, 20)
print(result)  # Output: 30

# Create Go type instance and call methods
counter = lib.new_type("Counter", 0)
print(counter.Incr(5))  # Output: 5
print(counter.Incr(3))  # Output: 8
print(counter.Value())  # Output: 8
```

Run the python script:

```bash
python main.py
```

## Go calling Python

### 1. Export Python Functions/Classes

```python
# main.py
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

if __name__ == "__main__":
    lib = gopylink.load_go_lib("go.lib")
    lib.func_call("Start")  # Start the Go logic
```

### 2. Call Python from Go

```go
package main

import (
	"fmt"
	"github.com/ray4go/gopylink"
)

type functions struct{}

func (functions) Start() {
	// Call Python function
	result := gopylink.PythonFuncCall("greet", "Gopher")
	val, err := result.Get()
	fmt.Printf("greet: %v, err: %v\n", val, err) // Output: greet: Hello, Gopher!, err: <nil>

	// Call with typed result
	result = gopylink.PythonFuncCall("multiply", 6, 7)
	product, err := gopylink.Get[int](result)
	fmt.Printf("multiply: %v, err: %v\n", product, err) // Output: multiply: 42, err: <nil>

	// Create Python class instance
	cnt := gopylink.NewPythonClassInstance("Counter", 10)
	defer cnt.Close()

	res := cnt.MethodCall("incr", 5)
	val, err = res.Get()
	fmt.Printf("Counter.incr: %v, err: %v\n", val, err) // Output: Counter.incr: 15, err: <nil>
}

func init() {
	gopylink.Init(functions{}, nil)
}

func main() {}
```

### 3. Build and Run

```bash
go build -buildmode=c-shared -o go.lib .
python main.py
```

Note that when calling Python from Go, the entry point remains the Python script. The Go shared library is loaded into the Python process, which then starts the Go logic.

## API Reference

### Python API

| Function                     | Description                                     |
|------------------------------|-------------------------------------------------|
| `load_go_lib(path)`          | Load a Go shared library                        |
| `lib.func_call(name, *args)` | Call a Go function by name                      |
| `lib.new_type(name, *args)`  | Create a Go type instance                       |
| `@export`                    | Decorator to export Python function/class to Go |

### Go API

| Function                                | Description                                  |
|-----------------------------------------|----------------------------------------------|
| `Init(funcRegister, classRegister)`     | Initialize and register Go functions/classes |
| `PythonFuncCall(name, args...)`         | Call a Python function                       |
| `NewPythonClassInstance(name, args...)` | Create a Python class instance               |
| `Get[T](result)`                        | Get typed result from Python call            |
| `result.Get()`                          | Get result as `(any, error)`                 |
| `handle.MethodCall(name, args...)`      | Call method on Python instance               |
| `handle.Close()`                        | Release Python instance                      |

See [Go API Reference](https://pkg.go.dev/github.com/ray4go/gopylink#pkg-index) for more details.

## Type Conversion

Types are automatically converted via msgpack:

| Go Type              | Python Type |
|----------------------|-------------|
| `int`, `int64`, etc. | `int`       |
| `float32`, `float64` | `float`     |
| `bool`               | `bool`      |
| `string`             | `str`       |
| `[]byte`             | `bytes`     |
| slice, array         | `list`      |
| `map`                | `dict`      |
| `struct`             | `dict`      |
| `nil`                | `None`      |

For detailed type conversion rules, see
the [Cross-Language Type Conversion Guide](https://github.com/ray4go/go-ray/blob/master/docs/crosslang_types.md).

## Thread Safety

GoPyLink operations are thread-safe. Multiple goroutines/threads can safely call cross-language functions concurrently.

## Performance Notes

Go FFI has approximately **30ns overhead** per call compared to native C/C++ FFI due to Go's virtual stack. This
overhead is:

- **Negligible** for coarse-grained operations
- **Significant** for micro-calls requiring millions of invocations per second

## Best Practices

**Golang Parameter and return types**

- Prefer concrete types (primitive types, composites, structs, and their pointers) over interface types for parameters
- Do not use interface types as return values except for `any` type.

**Golang Error handling**

Do not return `error` (as it is an interface) directly from Ray Task functon / Actor methods. Instead, return concrete
types to indicate errors (e.g., return int for error code), or just `panic` in your code.

When `ObjectRef.GetAll()` / `ObjectRef.Getinto()` / `ray.GetN(obj)` is called on a panic-ed task/actor, it will return an error.
You can use `fmt.Printf("%+v", err)` to print the error stack trace.

## License

MIT
