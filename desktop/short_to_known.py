#!/usr/bin/env python
"""
Intended to read a file with:
    ValChart,Survey,Mileage,Name
"""
import sys
import csv
import json

# O = Railroad Over -> Bridges, Culverts, etc
CLASS = "O"

with open(sys.argv[1], "r") as short_file:
    for line in csv.reader(short_file, delimiter=',', quotechar="'"):
        if len(line) == 0 or line[0].startswith("#"):
            continue
        if line[0] != "":
            val = line[0]
        survey = line[1]
        mileage = float(line[2])
        name = line[3]
        metadata = {
            "name": name,
            #"survey": survey,
            "val": val,
        }
        if survey != "":
            metadata['survey'] = survey

        print("- K - - %0.2f %s '%s' *" % (mileage, CLASS, json.dumps(metadata)))
