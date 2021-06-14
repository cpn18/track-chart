#!/usr/bin/env python3
"""
Calculates the average measurement [0..359]

Useful when trying to calibrate the angles for a new LIDAR position
"""
import sys
import json
import math
import statistics
import lidar_a1m8 as lidar_util

RANGE = 360 # degrees
OFFSET = 0
THRESHOLD = 500 # mm

MM_TO_INCH = 0.0393701

def ad_to_xy(a, d):
    x = d * math.sin(math.radians(a))
    y = d * math.cos(math.radians(a))
    return (x, y)

def my_min(data, threshold):
    retval = 999999
    for d in data:
        if d > threshold and d < retval:
            retval = d
    return retval

def main(filename):
    s = [0] * RANGE
    data = []
    for a in range(RANGE):
        data.append([])

    clearances = open("clearance.csv", "w")
    clearances.write("Date Time Clearance\n")

    with open(sys.argv[1], "r") as f:
        for line in f:
            obj = json.loads(line)
            if obj['class'] == "LIDAR":
                for angle, distance in obj['scan']:
                    distance = lidar_util.estimate_from_lidar(distance)
                    a = round(angle+OFFSET) % RANGE
                    d = float(distance)
                    if d > 0:
                        (x, y) = ad_to_xy(a, d)
                        s[a] = y
                        data[a].append(d)

                # Calculate ground clearance
                sample = s[150:210]
                clearance = -sum(sample)/len(sample)
                if (0 < clearance < 625):
                    clearances.write(
                        "%s %02f\n" %
                        (obj['time'].replace('T', ' ').replace('Z',''),
                            clearance*MM_TO_INCH)
                    )

    clearances.close()


    avgd = [0] * RANGE
    with open("average_lidar.csv", "w") as f:
        f.write("Angle,Distance,Trend,X,Y\n")
        for a in range(RANGE):
            if len(data[a]) > 0:
                d = statistics.mean(data[a]) 
                avgd[a] = d
            else:
                d = 0
            (x, y) = ad_to_xy(a, d)
            if a == 0:
                trend = 0
            elif d > avgd[a-1]:
                trend = 1
            elif d < avgd[a-1]:
                trend = -1
            else:
                trend = 0
            f.write("%d,%f,%d,%f,%f\n" % (a, d, trend, x, y))

    # find right rail
    a = 180-60
    while avgd[a] > avgd[a+1]:
        a += 1
    print("right", a)

    # find left rail
    a = 180+60
    while avgd[a] > avgd[a-1]:
        a -= 1
    print("left", a)

    with open("min_lidar.csv", "w") as f:
        f.write("Angle,Distance,X,Y\n")
        for a in range(RANGE):
            if len(data[a]) > 0:
                d = my_min(data[a], THRESHOLD) 
            else:
                d = 0
            (x, y) = ad_to_xy(a, d)
            f.write("%d,%f,%f,%f\n" % (a, d, x, y))

if len(sys.argv) != 2:
    print("USAGE: %s data_file.csv" % sys.argv[0])
    sys.exit(1)

main(sys.argv[1])
