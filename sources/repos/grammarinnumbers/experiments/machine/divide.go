package main

import (
	"fmt"
	"math"
	"os"
	"strconv"
)

func main() {
	a, _ := strconv.Atoi(os.Args[2])
	b, _ := strconv.Atoi(os.Args[3])
	switch os.Args[1] {
	case "int":
		fmt.Println(int32(a) / int32(b))
	case "min":
		fmt.Println(int32(math.MinInt32) / int32(b))
	case "f64":
		fmt.Println(float64(a) / float64(b))
	}
}
