#!/usr/bin/env python3
"""
Export As KML
"""
import os
import sys
import csv

import pirail

GPS_THRESHOLD = 10

filename = sys.argv[1]
output = filename.replace(".json", ".kml")

with open(output, "w") as kml:
    kml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    kml.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    kml.write('<Document>\n')
    kml.write('<Placemark>\n')
    kml.write('<name>'+os.path.basename(filename)+'</name>\n')
    kml.write('<LineString>\n')
    kml.write('<coordinates>\n')

    for line_no, obj in pirail.read(sys.argv[1], classes=['TPV']):
        if obj['num_used'] > GPS_THRESHOLD:
            kml.write("%f,%f,%f\n" % (
                obj['lon'],
                obj['lat'],
                obj['alt'],
                )
            )

    kml.write('</coordinates>\n')
    kml.write('</LineString>\n')
    kml.write('</Placemark>\n')
    kml.write('</Document>\n')
    kml.write('</kml>\n')

print("Output = %s" % output)
