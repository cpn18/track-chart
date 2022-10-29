#!/bin/bash
#
# USAGE: launch.sh [directory]

export PYTHONPATH=../desktop

# Check for external storage
external_storage=${1:-"/run/media/jminer/FreeAgent Drive/PIRAIL/20221015"}
if [ -d "${external_storage}" ]; then
    export PIRAILDATA="${PIRAILDATA:-${external_storage}}"
fi

echo "Using PIRAILDATA = ${PIRAILDATA}"
python3 web_server.py 8080
