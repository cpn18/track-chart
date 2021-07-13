import sys
import json
import datetime

TIME_THRESHOLD = 30

def parse_time(time_string):
    return datetime.datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")

try:
    filename = sys.argv[1]
except IndexError:
    print("USGAE: %s datafile.json" % sys.argv[0])
    sys.exit(1)

last_speed = None

with open(filename) as f:
    for line in f:
        try:
            obj = json.loads(line)
        except Exception as ex:
            print("LINE: %s" % line)
            print("ERROR: %s" % ex)
            sys.exit(1)

        if obj['class'] != "TPV":
            continue
        
        try:
            speed = obj['speed']
            eps = obj['eps']
            fix_time = parse_time(obj['time'])
        except KeyError:
            continue


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
