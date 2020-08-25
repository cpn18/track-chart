#!/usr/bin/env python3
"""
Export As KML
"""
import pickle
import os
import sys


with open(sys.argv[1]+".pickle","rb") as f:
    data = pickle.load(f)
    data = sorted(data, key=lambda k: k['time'], reverse=False)
    #data = sorted(data, key=lambda k: k['mileage'], reverse=False)


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
    for obj in data:
        if obj['type'] == 'G':
            if 'epx' in obj and 'epy' in obj:
                print(obj['epx'],obj['epy'])
                sumx += obj['epx']
                sumy += obj['epy']
                count += 1
                if obj['epx'] < 10 and obj['epy'] < 10:
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
