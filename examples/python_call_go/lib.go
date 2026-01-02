package main

import (
	"github.com/ray4go/gopylink"
)

// Functions to export - all exported methods become callable from Python
type functions struct{}

func (functions) Hello(name string) string {
	return "Hello " + name
}

func (functions) Add(a, b int) int {
	return a + b
}

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

func init() {
	gopylink.Init(functions{}, classes{})
}

func main() {}
