#!/bin/bash
# This script is used by netlify to the HTML page
set -e
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d
export GOPATH=$(go env GOPATH)
export PATH=$PATH:$GOPATH/bin
dir $GOPATH/bin
./bin/task --concurrency=1 render
