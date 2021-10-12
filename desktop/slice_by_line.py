#!/usr/bin/env python3
"""
Slice a datafile based on line number
"""
import sys
import json

import pirail

try:
    filename = sys.argv[-1]
    split_line_no = int(sys.argv[-2])
except IndexError:
    print("USAGE: %s [args] line_no data_file.json" % sys.argv[0])
    sys.exit(1)

outfile_name = filename.replace(".json", "_%d.json")

outfile = None

for line_no, obj in pirail.read(filename):
        
    if outfile is None or line_no == split_line_no:
        if outfile is not None:
            outfile.close()
        outfile = open(outfile_name % line_no, "w")
        print("Writing %s" % (outfile_name % line_no))

    outfile.write(json.dumps(obj)+"\n")

outfile.close()
