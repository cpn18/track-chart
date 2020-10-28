#!/usr/bin/env python3
"""
Calculates the average measurement [0..359]

Useful when trying to calibrate the angles for a new LIDAR position
"""
import sys
import math
import statistics
import json

RANGE = 360
OFFSET = 0

def main(filename):
    data = []
    for a in range(RANGE):
        data.append([])

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
                    print("%s %f %f %d %d" % (obj['time'], obj['lat'], obj['lon'], used, count))
                except KeyError:
                    pass
                used = count = 0
            else:
                continue

main(sys.argv[1])
