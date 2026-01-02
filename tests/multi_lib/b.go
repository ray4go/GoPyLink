package main

import (
	"github.com/ray4go/gopylink"
)

// classes to export - each method creates a new instance
type classes struct{}

type Counter struct {
	value int
}

func (classes) Counter(initial int) *Counter {
	return &Counter{value: initial}
}

func (c *Counter) Incr(n int) int {
	c.value += n
	return c.value
}

func (c *Counter) Value() int {
	return c.value
}

type bfunctions struct{}

func (bfunctions) CallPy(name string, args ...any) any {
	res, err := gopylink.PythonFuncCall(name, args...).Get()
	if err != nil {
		panic(err)
	}
	return res
}

func init() {
	gopylink.Init(bfunctions{}, classes{})
}

func main() {}
