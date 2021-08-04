#!/usr/bin/env python3
import sys
import json

import pirail

TIME_THRESHOLD = 30

try:
    filename = sys.argv[-1]
except IndexError:
    print("USAGE: %s [args] data_file.json" % sys.argv[0])
    sys.exit(1)

last_speed = None

print("Latitude Longitude Seconds")

for line_no, obj in pirail.read(filename,classes=['TPV']):
        
    if 'speed' not in obj or 'eps' not in obj or 'time' not in obj:
        continue

    speed = obj['speed']
    eps = obj['eps']
    fix_time = pirail.parse_time(obj['time'])

    if last_speed is None:
        last_speed = speed
        last_time = fix_time

    time_delta = (fix_time - last_time).total_seconds()

    if speed < eps and last_speed != 0 and time_delta > TIME_THRESHOLD:
        # we stopped
        last_speed = 0
        #print("Stopped: %s" % obj)
        print("%f %f %d" % (obj['lat'], obj['lon'], time_delta))
    elif speed > eps and last_speed == 0:
        # started to move again
        last_speed = speed
        last_time = fix_time
    else:
        # still stopped
        pass
