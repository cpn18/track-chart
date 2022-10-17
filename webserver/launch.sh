#!/bin/bash

export PYTHONPATH=../desktop

# Check for external storage - WORKAROUND
external_storage="/run/media/jminer/FreeAgent Drive/PIRAIL/20210725"
if [ -d "${external_storage}" ]; then
    export PIRAILDATA="${external_storage}"
fi

python3 web_server.py 8080
