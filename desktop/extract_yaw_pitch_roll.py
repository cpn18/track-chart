import sys
import json

print("Time", "Latitude", "Longitude", "Yaw", "Pitch", "Roll")
with open(sys.argv[1], "r") as f:
    for line in f:
        obj = json.loads(line)
        if 'roll' in obj:
            print(obj['time'], obj['lat'], obj['lon'], obj['yaw'], obj['pitch'], obj['roll'])

