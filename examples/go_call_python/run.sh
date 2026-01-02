#!/usr/bin/env bash

cd "$(dirname "$0")"
go build -buildmode=c-shared -o out/go.lib .
python app.py
