import sys
import json
import math

THRESHOLD = 10

data = []
with open(sys.argv[1], "r") as f:
    used = count = 0
    for line in f:
        if line[0] == "#":
            continue
        items = line.split()
        if items[1] == "TPV":
            obj = json.loads(" ".join(items[2:-1]))
            obj['used'] = used
            obj['count'] = count
        elif items[1] == "SKY":
            obj = json.loads(" ".join(items[2:-1]))
            used = 0
            count = len(obj['satellites'])
            for i in range(0, count):
                if obj['satellites'][i]['used']:
                    used += 1
            continue
        else:
            continue

        if used >= THRESHOLD and 'lon' in obj and 'lat' in obj:
            data.append(obj)

print("Longitude Latitude dx epx dy epy used count")
for i in range(1, len(data)):
    dx = abs((data[i]['lon'] - data[i-1]['lon']) * 111120 * math.cos(math.radians(data[i]['lat'])))
    dy = abs((data[i]['lat'] - data[i-1]['lat']) * 111128) # degrees to meters

    try:
        if dx > 3*data[i]['epx'] or dy > 3*data[i]['epy']:
            continue

        print("%f %f %f %f %f %f %d %d" % (data[i]['lon'], data[i]['lat'], dx, data[i]['epx'], dy, data[i]['epy'], data[i]['used'], data[i]['count']))
    except KeyError:
        pass
