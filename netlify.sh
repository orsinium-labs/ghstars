#!/bin/bash
# This script is used by netlify to build docs
set -e
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d
./bin/task fetch
./bin/task render
