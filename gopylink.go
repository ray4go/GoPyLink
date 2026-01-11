package gopylink

import (
	"github.com/ray4go/go-ray/ray"
)

// Init export golang functions and classes (types) to python.
//   - All exported methods on funcRegister are expose to python as functions and can be invoked via [PythonFuncCall].
//   - Exported methods on classRegister are used to expose golang class (types) to python; each method serves as the actor’s constructor.
//     The method must return exactly one value (the type instance), and should panic or return nil on failure to create the type.
//
// Call this function from the main package's init() function in your go code.
// All other GoPyLink APIs MUST be called after this function.
func Init(funcRegister any, classRegister any) {
	ray.Init(funcRegister, classRegister, nil)
}

// PythonResult represents the result of a Python function / method call.
type PythonResult ray.LocalPyCallResult

// Get returns the result of the Python call.
func (r PythonResult) Get() (any, error) {
	return ray.LocalPyCallResult(r).Get()
}

// PythonObjectHandle represents a handle to a Python class instance.
type PythonObjectHandle ray.PyLocalInstance

// MethodCall calls a method on the local Python class instance.
func (h *PythonObjectHandle) MethodCall(methodName string, args ...any) PythonResult {
	return PythonResult((*ray.PyLocalInstance)(h).MethodCall(methodName, args...))
}

// Close closes the Python class instance. So it can be garbage collected in Python side.
func (h *PythonObjectHandle) Close() error {
	return (*ray.PyLocalInstance)(h).Close()
}

// PythonFuncCall executes a Python function by name with the provided arguments.
func PythonFuncCall(name string, args ...any) PythonResult {
	return PythonResult(ray.LocalCallPyTask(name, args...))
}

// NewPythonClassInstance initializes a new Python class instance.
func NewPythonClassInstance(className string, args ...any) *PythonObjectHandle {
	return (*PythonObjectHandle)(ray.NewPyLocalInstance(className, args...))
}

// Get is used to get the result of python function / method call.
func Get[T any](obj PythonResult) (T, error) {
	return ray.Get1[T](ray.LocalPyCallResult(obj))
}
