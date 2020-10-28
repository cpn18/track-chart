import sys
import pickle

with open(sys.argv[1]+".pickle","rb") as f:
    data = pickle.load(f)

min_lat = 9999
min_lon = 9999
max_lat = -9999
max_lon = -9999

for obj in data:
    min_lat = min(min_lat, obj['lat'])
    max_lat = max(max_lat, obj['lat'])
    min_lon = min(min_lon, obj['lon'])
    max_lon = max(max_lon, obj['lon'])

print("min lat", min_lat)
print("max lat", max_lat)
print("min lon", min_lon)
print("max lon", max_lon)
