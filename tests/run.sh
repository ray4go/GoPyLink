#!/bin/bash

set -e

cd "$(dirname "$0")"

ls */run.sh | xargs -n 1 bash -e