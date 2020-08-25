#!/usr/bin/env python3
"""
Export As KML
"""
import os
import sys
import csv
import geo

def read_file(filename):
    data = []
    with open(filename, "r") as f:
        for line in csv.reader(f, delimiter=' ', quotechar="'"):
            if len(line) > 5 and line[1] =="G":
                data.append({
                    'time': line[0].split('.')[0],
                    'lat': float(line[2]),
                    'lon': float(line[3]),
                    })

    return data

d1 = read_file(sys.argv[1])
d2 = read_file(sys.argv[2])

i1=i2=0

count = 0
sumd = 0
mind = 9999
maxd = 0
while i1 < len(d1) and i2 < len(d2):
    if d1[i1]['time'] == d2[i2]['time']:
        print(d1[i1]['lat'], d1[i1]['lon'],d2[i2]['lat'], d2[i2]['lon'])
        d = geo.great_circle(
                d1[i1]['lat'], d1[i1]['lon'],
                d2[i2]['lat'], d2[i2]['lon'])
        sumd += d
        mind = min(mind, d)
        maxd = max(maxd, d)
        count += 1
        i1 += 1
        i2 += 1
    elif d1[i1]['time'] < d2[i2]['time']:
        print("skip 1")
        i1 += 1
    elif d1[i1]['time'] > d2[i2]['time']:
        print("skip 2")
        i2 += 1
    else:
        print(i1,d1[i1])
        print(i2,d1[i2])
        raise Exception
        
print("Count = %d" % count)
print("MinD = %f" % mind)
print("AvgD = %f" % (sumd/count))
print("MaxD = %f" % maxd)
