#!/usr/bin/env python3

import sys
import json

import pirail

print("Time Latitude Longitude Yaw Pitch Roll")
for line_no, obj in pirail.read(sys.argv[-1], classes=['ATT']):
    if 'roll' in obj:
        print("%s %f %f %f %f %f" % (
            obj['time'],
            obj['lat'],
            obj['lon'],
            obj['yaw'],
            obj['pitch'],
            obj['roll'],
            )
        )
