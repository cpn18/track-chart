#!/usr/bin/env python3
"""
Script to adjust mileages
"""

import sys
import json
import pirail

flip = add = None

i = 1
while i < len(sys.argv):
    if sys.argv[i] == "--flip":
        flip = float(sys.argv[i+1])
        i += 1
    elif sys.argv[i] == "--add":
        add = float(sys.argv[i+1])
        i += 1
    i += 1

for line_no, obj in pirail.read(sys.argv[-1]):
    if flip is not None:
        obj['mileage'] = flip - obj['mileage']
    elif add is not None:
        obj['mileage'] = obj['mileage'] + add

    print(json.dumps(obj))
