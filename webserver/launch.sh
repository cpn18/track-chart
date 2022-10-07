#!/bin/bash

export PYTHONPATH=../desktop

# Check for external storage - WORKAROUND
if [ -d "/run/media/jminer/FreeAgent Drive" ]; then
    export PIRAILDATA="/run/media/jminer/FreeAgent Drive/PIRAIL/20210725"
fi

python web_server.py 8080
