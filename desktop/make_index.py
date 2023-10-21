#!/usr/bin/env python3
"""
Build an index of locations
"""
import sys
import os
import gps_to_mileage
import json

index = {}

def contains(latitude, longitude):
    """ Returns name of dataset or None """
    for key in index:
        if index[key]['min_lat'] <= latitude <= index[key]['max_lat'] and \
                index[key]['min_lon'] <= longitude <= index[key]['max_lon']:
                    return key
    return None

for filename in sys.argv[1:]:
    G = gps_to_mileage.Gps2Miles(filename)
    name, ext = os.path.splitext(os.path.basename(filename))
    index[name] = {
        "min_lat": G.min_lat,
        "max_lat": G.max_lat,
        "min_lon": G.min_lon,
        "max_lon": G.max_lon,
    }

#print(index)

rootdir = os.path.join(os.environ['HOME'], "PIRAIL")

for root, dirnames, filenames in os.walk(rootdir):
    for filename in filenames:
        if not (filename.endswith(".json") or filename.endswith("_gps.csv")):
            continue
        fullpathname = os.path.join(root,filename)
        min_lat = 90
        max_lat = -90
        min_lon = 180
        max_lon = -180
        with open(fullpathname) as infile:
            for line in infile:
                line = line.strip()
                try:
                    if len(line) == 0 or line[0] == "#":
                        # Ignore blank and comments
                        continue
                    elif line[0] == "{":
                        # New style JSON
                        obj = json.loads(line)
                    else:
                        # Old Style CSV
                        items = line.strip().replace("'", "\"").split(" ")
                        obj = json.loads(" ".join(items[2:-1]))

                except Exception as ex:
                    print(ex)
                    print(line)
                    sys.exit(1)

                # Check for a fix
                if not 'class' in obj or \
                    obj['class'] != 'TPV' or \
                    not 'lat' in obj:
                    continue

                min_lat = min(min_lat, obj['lat'])
                max_lat = max(max_lat, obj['lat'])
                min_lon = min(min_lon, obj['lon'])
                max_lon = max(max_lon, obj['lon'])

                # Is the point inside a geo-fence?
                place = contains(obj['lat'], obj['lon'])
                if place is None:
                    continue

                if place != "office":
                    print(fullpathname, place)
                break

        if place is None:
            print(fullpathname, "UNKNOWN", min_lat, min_lon, max_lat, max_lon)
