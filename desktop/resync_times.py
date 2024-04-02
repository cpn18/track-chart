#!/usr/bin/env python3
"""
Resync Time

Utility to normalize time
"""
import os
import sys
import json

import pirail

if len(sys.argv) < 2:
    print("USAGE: %s [args] data_file.json" % sys.argv[0])
    sys.exit(1)

filename = sys.argv[-1]

basetime = None

for line_no, obj in pirail.read(sys.argv[-1]):
    if basetime is None:
        basetime = pirail.parse_time(obj['time'])
    timediff = pirail.parse_time(obj['time']) - basetime
    obj['time'] = timediff
    print(json.dumps(obj))
