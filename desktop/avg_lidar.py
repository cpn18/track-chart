#!/usr/bin/env python3
import sys
import math
import gps_to_mileage

OFFSET=2.6

def main(filename):
    data = [0] * 360
    count = [0] * 360

    with open(sys.argv[1], "r") as f:
        for line in f:
            if line[0] == "#":
                continue
            if line[-2] != "*":
                continue
            fields = line.split(" ")
            if fields[1] == "L":
                timestamp, datatype, scan_data = line.split(" ", 2)
                scan_data = eval(scan_data.replace('*', ''))
                for angle, distance in scan_data:
                    i = round(float(angle+OFFSET)) % 360
                    data[i] += float(distance)
                    count[i] += 1 

    for a in range(360):
        d = data[a]/count[a]
        x = d * math.sin(math.radians(a))
        y = d * math.cos(math.radians(a))

        print("%d %f %f %f" % (a, d, x, y))

main(sys.argv[1])
