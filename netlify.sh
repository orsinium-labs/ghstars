#!/bin/bash
# This script is used by netlify to the HTML page
set -e
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d
dir /opt/buildhome/.gimme/versions/go1.19.7.linux.amd64/bin
./bin/task --concurrency=1 render
