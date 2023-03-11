#!/bin/bash
# This script is used by netlify to the HTML page
set -e
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d
echo $PATH
./bin/task --concurrency=1 render
