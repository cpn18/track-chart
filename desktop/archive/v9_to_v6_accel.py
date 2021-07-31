#!/usr/bin/env python

import sys
import json

lasttime = None

print("#v6")
with open(sys.argv[1], "r") as input_file:
    line = input_file.readline().strip()
    if line != "#v9":
        sys.exit(1)
    for line in input_file:
        fields = line.strip().split()
        if fields[1] != 'ATT' or fields[-1] != '*':
            continue

        obj = json.loads(" ".join(fields[2:-1]))
    
        timestamp = fields[0].split('.')[0]
        if lasttime is None:
            lasttime = timestamp
            sumx = minx = maxx = obj['acc_x']
            sumy = miny = maxy = obj['acc_y']
            sumz = minz = maxz = obj['acc_y']
            count = 1
            continue

        if timestamp == lasttime:
            x = obj['acc_x'] 
            y = obj['acc_y'] 
            z = obj['acc_z'] 
            sumx += x
            minx = min(minx, x)
            maxx = max(maxx, x)
            sumy += y
            miny = min(miny, y)
            maxy = max(maxy, y)
            sumz += z
            minz = min(minz, z)
            maxz = max(maxz, z)
            count += 1
            continue

        lasttime = timestamp
        print("%s.000Z A %d %f %f %f %f %f %f %f %f %f *" % (lasttime, count, minx, sumx/count, maxx, miny, sumy/count, maxy, minz, sumz/count, maxz))
        sumx = minx = maxx = obj['acc_x']
        sumy = miny = maxy = obj['acc_y']
        sumz = minz = maxz = obj['acc_z']
        count = 1

    print("%s.000Z A %d %f %f %f %f %f %f %f %f %f *" % (lasttime, count, minx, sumx/count, maxx, miny, sumy/count, maxy, minz, sumz/count, maxz))
