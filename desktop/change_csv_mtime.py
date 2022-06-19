#!/usr/bin/env python3
"""
Recalculate Mtime

Uses either the time from a filename, assumed to start
with YYYYmmddHHMMSS_, or by reading the last data
element in the CSV file
"""
import sys
import os
import datetime
from dateutil.parser import parse

def change_mtime(filename):
    """ Alter timestamps in files """
    timestamp = os.path.basename(filename).split("_")[0]
    with open(filename, "r") as f_in:
        for line in f_in:
            timestamp = line.split(" ")[0]

    atime = datetime.datetime.utcnow()
    mtime = parse(timestamp, fuzzy=True)
    os.utime(filename, (atime.timestamp(), mtime.timestamp()))

if __name__ == "__main__":
    for f in sys.argv[1:]:
        change_mtime(f)
