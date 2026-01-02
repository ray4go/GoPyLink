#!/usr/bin/env bash

set -e

cd "$(dirname "$0")"

go build -buildmode=c-shared -o out/a.lib a.go
go build -buildmode=c-shared -o out/b.lib b.go
go build -buildmode=c-shared -o out/c.lib c.go

python main.py
