# GoPyLink

A lightweight Python & Go cross-language call framework for in-process communication.

GoPyLink enables seamless bidirectional function and method calls between Python and Go within the same process.

## Features

- **Python Call Go** - Call Go functions, create Go type instances and invoke methods
- **Go Call Python** - Call Python functions, create Python class instances and invoke methods
- **Simple API** - Minimal setup with intuitive interfaces

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

## Quick Start

### 1. Write Go Code

Create a `main.go` file:

```go
package main

import "github.com/ray4go/go-ray/gopylink"

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
go build -buildmode=c-shared -o mylib.so .
```

### 3. Call Go from Python

```python
from gopylink import load_go_lib

# Load the Go library
lib = load_go_lib("./mylib.so")

# Call Go functions
result = lib.func_call("Hello", "World")
print(result)  # Output: Hello World

result = lib.func_call("Add", 10, 20)
print(result)  # Output: 30

# Create Go type instance and call methods
counter = lib.new_type("Counter", 0)
print(counter.Incr(5))   # Output: 5
print(counter.Incr(3))   # Output: 8
print(counter.Value())   # Output: 8
```

## Go Call Python

GoPyLink also supports calling Python from Go.

### 1. Define Python Functions/Classes

```python
from gopylink import export

@export
def greet(name: str) -> str:
    return f"Hi, {name}!"

@export
def multiply(a, b):
    return a * b

@export
class Calculator:
    def __init__(self, initial=0):
        self.value = initial

    def add(self, n):
        self.value += n
        return self.value
```

### 2. Call from Go

```go
package main

import (
    "fmt"
    "github.com/ray4go/go-ray/gopylink"
)

type Functions struct{}

func (Functions) CallPythonDemo() {
    // Call Python function
    result := gopylink.PythonFuncCall("greet", "Gopher")
    val, _ := result.Get()
    fmt.Println(val)  // Output: Hi, Gopher!

    // Call with typed result
    product, _ := gopylink.Get[int](gopylink.PythonFuncCall("multiply", 6, 7))
    fmt.Println(product)  // Output: 42

    // Create Python class instance
    calc := gopylink.NewPythonClassInstance("Calculator", 10)
    defer calc.Close()

    res := calc.MethodCall("add", 5)
    val, _ = res.Get()
    fmt.Println(val)  // Output: 15
}

func init() {
    gopylink.Init(Functions{}, nil)
}

func main() {}
```

### 3. Run from Python

```python
from gopylink import load_go_lib, export

# Define Python functions first
@export
def greet(name: str) -> str:
    return f"Hi, {name}!"

@export
def multiply(a, b):
    return a * b

# Load Go library and call
lib = load_go_lib("./mylib.so")
lib.func_call("CallPythonDemo")
```

## API Reference

### Python API

| Function | Description |
|----------|-------------|
| `load_go_lib(path)` | Load a Go shared library, returns a `CrossLanguageClient` |
| `lib.func_call(name, *args)` | Call a Go function by name |
| `lib.new_type(name, *args)` | Create a Go type instance |
| `@export` | Decorator to export Python function/class to Go |

### Go API

| Function | Description |
|----------|-------------|
| `Init(funcRegister, classRegister)` | Initialize and register Go functions/classes |
| `PythonFuncCall(name, args...)` | Call a Python function |
| `NewPythonClassInstance(name, args...)` | Create a Python class instance |
| `Get[T](result)` | Get typed result from Python call |
| `result.Get()` | Get result as `(any, error)` |
| `handle.MethodCall(name, args...)` | Call method on Python instance |
| `handle.Close()` | Release Python instance |

## Type Conversion

Types are automatically converted via msgpack:

| Go Type | Python Type |
|---------|-------------|
| `int`, `int64`, etc. | `int` |
| `float32`, `float64` | `float` |
| `bool` | `bool` |
| `string` | `str` |
| `[]byte` | `bytes` |
| slice, array | `list` |
| `map` | `dict` |
| `struct` | `dict` |
| `nil` | `None` |

For detailed type conversion rules, see the [Cross-Language Type Conversion Guide](https://github.com/ray4go/go-ray/blob/master/docs/crosslang_types.md).

## Complete Example

**app.go:**
```go
package main

import (
    "fmt"
    "github.com/ray4go/go-ray/gopylink"
)

type Functions struct{}

func (Functions) Echo(args ...any) []any {
    return args
}

func (Functions) GoCallsPython() {
    result := gopylink.PythonFuncCall("process", "data from go")
    val, _ := result.Get()
    fmt.Printf("Python returned: %v\n", val)
}

type Classes struct{}

type Storage struct {
    data map[string]any
}

func (Classes) Storage() *Storage {
    return &Storage{data: make(map[string]any)}
}

func (s *Storage) Set(key string, value any) {
    s.data[key] = value
}

func (s *Storage) Get(key string) any {
    return s.data[key]
}

func init() {
    gopylink.Init(Functions{}, Classes{})
}

func main() {}
```

**main.py:**
```python
from gopylink import load_go_lib, export

@export
def process(data):
    return f"Processed: {data}"

lib = load_go_lib("./app.so")

# Python calls Go
print(lib.func_call("Echo", 1, "hello", [1, 2, 3]))

# Go calls Python
lib.func_call("GoCallsPython")

# Use Go class from Python
storage = lib.new_type("Storage")
storage.Set("key1", {"nested": "value"})
print(storage.Get("key1"))
```

**Build and run:**
```bash
go build -buildmode=c-shared -o app.so .
python main.py
```

## Thread Safety

GoPyLink operations are thread-safe. Multiple goroutines/threads can safely call cross-language functions concurrently.

## Performance Notes

Go FFI has approximately **30ns overhead** per call compared to native C/C++ FFI due to Go's virtual stack. This overhead is:
- **Negligible** for coarse-grained operations
- **Significant** for micro-calls requiring millions of invocations per second

## Limitations

- Only positional arguments supported (no keyword arguments)
- Interface types (`interface{}`) should be avoided in Go signatures
- Go `error` type not supported as return value (use string/int error codes instead)
- Recursive data structures may cause msgpack serialization issues

## License

MIT
