#!/usr/bin/env python3
"""
Useful when debugging GPS issues
"""
import sys
import math
import statistics
import json

import pirail

def main(filename):
    used=count=0

    print("Time Latitude Longitude Used Count")
    for line_no, obj in pirail.read(filename, classes=['SKY', 'TPV']):
        if obj['class'] == "SKY":
            used=count=0
            for s in obj['satellites']:
                count += 1
                if s['used']:
                    used += 1
        elif obj['class'] == "TPV":
            if 'num_sat' in obj:
                count = obj['num_sat']
            if 'num_used' in obj:
                used = obj['num_used']
            if 'lat' in obj and 'lon' in obj:
                if used >= pirail.GPS_THRESHOLD:
                    print("%s %f %f %d %d" % (obj['time'], obj['lat'], obj['lon'], used, count))

if len(sys.argv) < 2:
    print("USAGE: %s [args] data_file.json" % sys.argv[0])
    sys.exit(1)

main(sys.argv[-1])
