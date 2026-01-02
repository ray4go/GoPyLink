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
