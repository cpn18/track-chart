#!/bin/bash

export PYTHONPATH=../desktop

# Check for external storage - WORKAROUND
export PIRAILDATA="${HOME}/PIRAIL:${PWD}/PIRAIL"

python3 web_server.py 8080
