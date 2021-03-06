#!/usr/bin/env python3
"""
Calculates the average measurement [0..359]

Useful when trying to calibrate the angles for a new LIDAR position
"""
import sys
import json
import math
import statistics

RANGE = 360
OFFSET = 0

def my_min(data, threshold):
    retval = 999999
    for d in data:
        if d > threshold and d < retval:
            retval = d
    return retval

def main(filename):
    s = [0] * 360
    data = []
    for a in range(RANGE):
        data.append([])

    clearances = open("clearance.csv", "w")
    clearances.write("Date Time Clearance\n")

    with open(sys.argv[1], "r") as f:
        for line in f:
            if line[0] == "#":
                continue
            if line[-2] != "*":
                continue
            fields = line.split(" ")
            if fields[1] == "L" or fields[1] == "LIDAR":
                if fields[1] == "LIDAR":
                    lidar = json.loads(" ".join(fields[2:-1]))
                    timestamp = lidar['time']
                    scan_data = lidar['scan']
                else:
                    timestamp, datatype, scan_data = line.split(" ", 2)
                    scan_data = eval(scan_data.replace('*', ''))
                for angle, distance in scan_data:
                    a = round(angle+OFFSET) % RANGE
                    d = float(distance)
                    if d > 0:
                        x = d * math.sin(math.radians(a))
                        y = d * math.cos(math.radians(a))
                        s[a] = y
                        data[a].append(d)

                # Calculate ground clearance
                sample = s[150:210]
                clearance = -sum(sample)/len(sample)
                if (0 < clearance < 625):
                    clearances.write(
                        "%s %02f\n" %
                        (timestamp.replace('T', ' ').replace('Z',''),
                            clearance*0.0393701)
                    )

    clearances.close()

    with open("average_lidar.csv", "w") as f:
        f.write("Angle,Distance,X,Y\n")
        for a in range(RANGE):
            if len(data[a]) > 0:
                d = statistics.mean(data[a]) 
            else:
                d = 0
            x = d * math.sin(math.radians(a))
            y = d * math.cos(math.radians(a))
            f.write("%d,%f,%f,%f\n" % (a, d, x, y))

    with open("min_lidar.csv", "w") as f:
        f.write("Angle,Distance,X,Y\n")
        for a in range(RANGE):
            if len(data[a]) > 0:
                d = my_min(data[a],500) 
            else:
                d = 0
            x = d * math.sin(math.radians(a))
            y = d * math.cos(math.radians(a))
            f.write("%d,%f,%f,%f\n" % (a, d, x, y))

if len(sys.argv) != 2:
    print("USAGE: %s data_file.csv" % sys.argv[0])
    sys.exit(1)

main(sys.argv[1])
