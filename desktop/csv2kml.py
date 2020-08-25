#!/usr/bin/env python3
"""
Export As KML
"""
import os
import sys
import csv


with open(sys.argv[1]+".kml", "w") as kml:
    kml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    kml.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    kml.write('<Document>\n')
    kml.write('<Placemark>\n')
    kml.write('<name>'+os.path.basename(sys.argv[1])+'</name>\n')
    kml.write('<LineString>\n')
    kml.write('<coordinates>\n')

    with open(sys.argv[1], "r") as f:
        for line in csv.reader(f, delimiter=' ', quotechar="'"):
            if len(line) > 5 and line[1] =="G":
                try:
                    kml.write("%f,%f,%f\n" % (float(line[3]),float(line[2]),float(line[4])))
                except ValueError:
                    pass

    kml.write('</coordinates>\n')
    kml.write('</LineString>\n')
    kml.write('</Placemark>\n')
    kml.write('</Document>\n')
    kml.write('</kml>\n')
