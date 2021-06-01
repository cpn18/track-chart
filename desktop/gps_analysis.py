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
            if line[0] == "#":
                continue
            if line[-2] != "*":
                continue
            fields = line.split(" ")

            if fields[1] == "SKY":
                obj = json.loads(" ".join(fields[2:-1]))
                used=count=0
                for s in obj['satellites']:
                    count += 1
                    if s['used']:
                        used += 1
            elif fields[1] == "TPV":
                obj = json.loads(" ".join(fields[2:-1]))
                try:
                    if used >= THRESHOLD:
                        print("%s %f %f %d %d" % (obj['time'], obj['lat'], obj['lon'], used, count))
                except KeyError:
                    pass
                #used = count = 0
            else:
                continue

if len(sys.argv) < 2:
    print("USAGE: %s data_file" % sys.argv[0])
    sys.exit(1)

main(sys.argv[1])
