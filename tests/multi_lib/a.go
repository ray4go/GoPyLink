package main

import (
	"fmt"
	"github.com/ray4go/gopylink"
)

type functions struct{}

func (functions) Divide(a, b int64) (int64, int64) {
	return a / b, a % b
}

func (functions) NoReturnVal(a, b int64) {
	return
}

type Point struct {
	X, Y int
}

// 2参数
func (functions) Add2Points(p1, p2 Point) Point {
	fmt.Println("PointAdd2", p1, p2)
	return Point{
		X: p1.X + p2.X,
		Y: p1.Y + p2.Y,
	}
}

func (functions) CallPy(name string, args ...any) any {
	res, err := gopylink.PythonFuncCall(name, args...).Get()
	if err != nil {
		panic(err)
	}
	return res
}

func init() {
	gopylink.Init(functions{}, nil)
}

func main() {}
