#!/usr/bin/env python3
"""
Export As KML
"""
import pickle
import os
import sys
import json


#with open(sys.argv[1]+".pickle","rb") as f:
#    data = pickle.load(f)
#    data = sorted(data, key=lambda k: k['time'], reverse=False)
#    #data = sorted(data, key=lambda k: k['mileage'], reverse=False)

data = []
with open(sys.argv[1], "r") as f:
    for line in f:
        if line[0] == "#":
            continue
        items = line.split()
        if items[1] == "TPV":
            obj = json.loads(" ".join(items[2:-1]))
        elif items[1] == "SKY":
            obj = json.loads(" ".join(items[2:-1]))
        else:
            continue
        obj['type'] = items[1]
        data.append(obj)


with open(sys.argv[1]+".kml", "w") as kml:
    kml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    kml.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    kml.write('<Document>\n')
    kml.write('<Placemark>\n')
    kml.write('<name>'+os.path.basename(sys.argv[1])+'</name>\n')
    kml.write('<LineString>\n')
    kml.write('<coordinates>\n')

    sumx = sumy = count = 0
    alt = 0
    used = 0
    for obj in data:
        if obj['type'] == 'SKY':
            used=0
            for s in obj['satellites']:
                if s['used']:
                    used += 1
            print(used, len(obj['satellites']))

        elif used >= 10 and obj['type'] == 'TPV':
            if 'speed' in obj and 'epx' in obj and 'epy' in obj:
                if obj['speed'] < 0.5:
                    continue
                print(obj['epx'],obj['epy'])
                sumx += obj['epx']
                sumy += obj['epy']
                count += 1
                if obj['epx'] < 100 and obj['epy'] < 100:
                    if 'alt' in obj:
                        kml.write("%f,%f,%f\n" % (obj['lon'],obj['lat'], obj['alt']))
                        alt = obj['alt']
                    else:
                        kml.write("%f,%f,%f\n" % (obj['lon'],obj['lat'],alt))

    kml.write('</coordinates>\n')
    kml.write('</LineString>\n')
    kml.write('</Placemark>\n')
    kml.write('</Document>\n')
    kml.write('</kml>\n')

    print("epx=%f" % (sumx/count))
    print("epy=%f" % (sumy/count))
