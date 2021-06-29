#!/usr/bin/env python3
"""
Useful when debugging GPS issues
"""
import sys
import math
import statistics
import json

THRESHOLD = 0

def main(filename):

    print("Time Latitude Longitude Used Count")
    with open(sys.argv[1], "r") as f:
        used = count = 0
        for line in f:
            obj = json.loads(line)

            if obj['class'] == "SKY":
                used=count=0
                for s in obj['satellites']:
                    count += 1
                    if s['used']:
                        used += 1
            elif obj['class'] == "TPV":
                try:
                    if used >= THRESHOLD:
                        print("%s %f %f %d %d" % (obj['time'], obj['lat'], obj['lon'], used, count))
                except KeyError:
                    pass
                #used = count = 0
            else:
                continue

if len(sys.argv) < 2:
    print("USAGE: %s datafile.json" % sys.argv[0])
    sys.exit(1)

main(sys.argv[1])
