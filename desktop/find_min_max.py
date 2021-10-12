#!/usr/bin/env python3
"""
Find the min/max bounding box
"""
import sys
import json

import pirail

try:
    filename = sys.argv[-1]
except IndexError:
    print("USAGE: %s [args] data_file.json" % sys.argv[0])
    sys.exit(1)

min_lat = 90
max_lat = -90
min_lon = 180
max_lon = -180

for line_no, obj in pirail.read(filename,classes=['TPV']):
        
    if obj['lat'] < min_lat:
        min_lat = obj['lat']
        min_lat_line = line_no

    if obj['lat'] > max_lat:
        max_lat = obj['lat']
        max_lat_line = line_no

    if obj['lon'] < min_lon:
        min_lon = obj['lon']
        min_lon_line = line_no

    if obj['lon'] > max_lon:
        max_lon = obj['lon']
        max_lon_line = line_no

print("Max Latitude: %f Line=%d" % (max_lat, max_lat_line))
print("Min Latitude: %f Line=%d" % (min_lat, min_lat_line))
print("Max Longitude: %f Line=%d" % (max_lon, max_lon_line))
print("Min Longitude: %f Line=%d" % (min_lon, min_lon_line))
