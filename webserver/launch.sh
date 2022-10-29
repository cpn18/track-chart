#!/bin/bash
#
# USAGE: launch.sh [directory1][:directory2]...[:directioryN]

export PYTHONPATH=../desktop

# Check for external storage
external_storage=${1:-"${HOME}/PIRAIL:${PWD}/PIRAIL"}
export PIRAILDATA=${PIRAILDATA:-${external_storage}}

echo "Using PIRAILDATA = ${PIRAILDATA}"
python3 web_server.py 8080
