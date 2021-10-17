#!/usr/bin/env python3
"""
GPS Smoothing
"""
import sys
import json
import math

import pirail

data = []
for line_no,obj in pirail.read(sys.argv[-1], classes=['SKY', 'TPV']):
    if obj['class'] == "TPV":
        if obj['num_used'] >= pirail.GPS_THRESHOLD and 'lon' in obj and 'lat' in obj:
            data.append(obj)
    elif obj['class'] == "SKY":
        used = count = 0
        count = len(obj['satellites'])
        for i in range(0, count):
            if obj['satellites'][i]['used']:
                used += 1

print("Longitude Latitude dx epx dy epy used count")
for i in range(1, len(data)):
    if 'exp' not in data[i] or 'epy' not in data[i]:
        continue

    dx = abs((data[i]['lon'] - data[i-1]['lon']) * 111120 * math.cos(math.radians(data[i]['lat'])))
    dy = abs((data[i]['lat'] - data[i-1]['lat']) * 111128) # degrees to meters

    if dx > 3*data[i]['epx'] or dy > 3*data[i]['epy']:
        continue

    print("%f %f %f %f %f %f %d %d" % (data[i]['lon'], data[i]['lat'], dx, data[i]['epx'], dy, data[i]['epy'], data[i]['used'], data[i]['count']))
