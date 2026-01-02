package main

import (
	"github.com/ray4go/gopylink"
)

type cfunctions struct{}

func (cfunctions) CallPy(name string, args ...any) any {
	res, err := gopylink.PythonFuncCall(name, args...).Get()
	if err != nil {
		panic(err)
	}
	return res
}

type cclasses struct{}

type handle gopylink.PythonObjectHandle

func (cclasses) NewPyObj(className string, args ...any) *handle {
	h := gopylink.NewPythonClassInstance(className, args...)
	return (*handle)(h)
}

func (h *handle) MethodCall(methodName string, args ...any) any {
	res, err := gopylink.PythonResult((*gopylink.PythonObjectHandle)(h).MethodCall(methodName, args...)).Get()
	if err != nil {
		panic(err)
	}
	return res
}

func init() {
	gopylink.Init(cfunctions{}, cclasses{})
}

func main() {}
