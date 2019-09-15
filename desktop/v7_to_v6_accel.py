#!/usr/bin/env python

import sys

lasttime = None

print "#v6"
with open(sys.argv[1], "r") as v7file:
    line = v7file.readline().strip()
    if line != "#v7":
        sys.exit(1)
    for line in v7file:
        fields = line.strip().split()
        if fields[1] != 'A' or fields[5] != '*':
            continue
    
        timestamp = fields[0].split('.')[0]
        if lasttime is None:
            lasttime = timestamp
            sumx = minx = maxx = float(fields[2])
            sumy = miny = maxy = float(fields[3])
            sumz = minz = maxz = float(fields[4])
            count = 1
            continue

        if timestamp == lasttime:
            x = float(fields[2])
            y = float(fields[3])
            z = float(fields[4])
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
        print "%s.000Z A %d %f %f %f %f %f %f %f %f %f *" % (lasttime, count, minx, sumx/count, maxx, miny, sumy/count, maxy, minz, sumz/count, maxz)
        sumx = minx = maxx = float(fields[2])
        sumy = miny = maxy = float(fields[3])
        sumz = minz = maxz = float(fields[4])
        count = 1

    print "%s.000Z A %d %f %f %f %f %f %f %f %f %f *" % (lasttime, count, minx, sumx/count, maxx, miny, sumy/count, maxy, minz, sumz/count, maxz)
