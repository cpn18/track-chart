#!/usr/bin/env python3
"""
Useful when debugging GPS issues
"""
import sys
import math
import statistics
import json

import geo
import pirail

def main(filename):
    used=count=0

    last_tpv = None
    print("Time Latitude Longitude Used Count Delta")
    for line_no, obj in pirail.read(filename, classes=['SKY', 'TPV'], args={"gps-threshold": 0}):
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
                if last_tpv is None:
                    delta = 0
                else:
                    delta = geo.great_circle(last_tpv['lat'],last_tpv['lon'],obj['lat'],obj['lon'])
                print("%s %f %f %d %d %f" % (obj['time'], obj['lat'], obj['lon'], used, count, delta))
                last_tpv = obj

if len(sys.argv) < 2:
    print("USAGE: %s [args] data_file.json" % sys.argv[0])
    sys.exit(1)

main(sys.argv[-1])
