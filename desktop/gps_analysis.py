#!/usr/bin/env python3
"""
Useful when debugging GPS issues
"""
import sys
import math
import statistics
import json

import pirail

GPS_THRESHOLD = 0

def main(filename):

    print("Time Latitude Longitude Used Count")
    for line_no, obj in pirail.read(sys.argv[1], classes=['SKY', 'TPV']):
        if obj['class'] == "SKY":
            used=count=0
            for s in obj['satellites']:
                count += 1
                if s['used']:
                    used += 1
        elif obj['class'] == "TPV":
            if 'lat' not in obj or 'lon' not in obj:
                if used >= GPS_THRESHOLD:
                    print("%s %f %f %d %d" % (obj['time'], obj['lat'], obj['lon'], used, count))

if len(sys.argv) < 2:
    print("USAGE: %s datafile.json" % sys.argv[0])
    sys.exit(1)

main(sys.argv[1])
