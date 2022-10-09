#!/bin/bash

export PYTHONPATH=../desktop

# Check for external storage - WORKAROUND
export PIRAILDATA="/run/media/jminer/FreeAgent Drive/PIRAIL:/home/jminer/track-chart/webserver/PIRAIL"

python web_server.py 8080
