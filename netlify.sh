#!/bin/bash
# This script is used by netlify to the HTML page
set -e
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d
./bin/task render ENC=/opt/buildhome/.gimme_cache/gopath/bin/enc
