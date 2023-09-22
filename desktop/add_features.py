#!/usr/bin/env python3
"""
Reads A Feature File
Adds to Known.CSV
"""

import sys
import gps_to_mileage
import csv
import json

gps = gps_to_mileage.Gps2Miles(sys.argv[1])

objclass = "O"  # Railroad Over

with open(sys.argv[2]) as infile:
    reader = csv.reader(infile, delimiter=' ', quotechar='"')
    for row in reader:
        obj = {
            "survey": row[0],
            "name": row[1],
            "val": row[2],
        }
        mileage = gps.survey_to_mileage(row[0])
        print("- K - - %f %s '%s' *" % (mileage, objclass, json.dumps(obj)))

