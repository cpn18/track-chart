#!/usr/bin/env python3
import json
import sys
import geo
import gps_to_mileage
import datetime

import pirail

if len(sys.argv) < 3:
    print("USAGE: %s [args] json_file known_file" % sys.argv[0])
    sys.exit(1)

json_file = sys.argv[-2]
known_file = sys.argv[-1]

GPS_THRESHOLD = 0
GPS_MIN_MODE = 3

GPS = gps_to_mileage.Gps2Miles(known_file)

acclist = []
data = []
last_tpv = None

for line_no, obj in pirail.read(json_file):
    if obj['class'] in ["SKY", "ATT", "LIDAR", "LPCM"]:
        acclist.append(obj)
    elif obj['class'] == "TPV":
        if obj['num_used'] < GPS_THRESHOLD or obj['mode'] < GPS_MIN_MODE:
            continue
        if last_tpv is not None:
            if len(acclist) > 0:
                time_start = pirail.parse_time(obj['time'])
                time_delta = time_start - pirail.parse_time(last_tpv['time'])
                delta_lat = (obj['lat'] - last_tpv['lat'])
                delta_lon = (obj['lon'] - last_tpv['lon'])
                delta_alt = (obj['alt'] - last_tpv['alt'])
                #print ("delta_lat", delta_lat)
                #print ("delta_lon", delta_lon)
                #print ("time_delta", time_delta.total_seconds())
                for acc in acclist:
                    acc_time = pirail.parse_time(acc['time'])

                    millsec = (acc_time - time_start).total_seconds() / time_delta.total_seconds()

                    acc['lat'] = last_tpv['lat'] + millsec*delta_lat
                    acc['lon'] = last_tpv['lon'] + millsec*delta_lon
                    acc['alt'] = last_tpv['alt'] + millsec*delta_alt
                    acc['mileage'], acc['certainty'] = GPS.find_mileage(acc['lat'], acc['lon'])
                    data.append(acc)
        obj['mileage'], obj['certainty'] = GPS.find_mileage(obj['lat'], obj['lon'])
        data.append(obj)
        last_tpv = obj
        acclist = []

print("Leftover elements = %d" % len(acclist))

# Sort By
#sortby='mileage'
SORTBY='time'
if SORTBY != 'time':
    data = sorted(data, key=lambda k: k[SORTBY], reverse=False)

with open(json_file.replace(".json", "_with_mileage_sort_by_%s.json" % SORTBY), "w") as f:
    for obj in data:
        f.write(json.dumps(obj)+"\n")

new_data = []
accset = []

# Find Starting Mileage
current = 0
step = 0.001
while True:
    if not 'mileage' in data[current]:
        current += 1
    else:
        start_mileage = round(data[current]['mileage'],2)
        next_mileage = start_mileage + step
        break

while current < len(data):
    if not 'mileage' in data[current]:
        current += 1
        continue

    if round(data[current]['mileage'],2) < next_mileage:
        accset.append(data[current])
        current += 1
    else:
        acc_z = -9999
        for a in accset:
            if a['class'] != "ATT":
                continue
            if a['acc_z'] > acc_z:
                acc_z = a['acc_z']
        if acc_z != -9999:
            new_data.append({'class': "ATT", 'mileage': start_mileage, 'acc_z': acc_z, 'lat': data[current]['lat'], 'lon': data[current]['lon']})
        accset = []
        start_mileage = next_mileage
        next_mileage += step

with open("acc_by_mileage.json", "w") as f:
    for obj in new_data:
        f.write(json.dumps(obj)+"\n")

with open("acc_by_mileage.csv", "w") as f:
    f.write("Mileage Latitude Longitude ACCz\n")
    for d in new_data:
        if d['class'] == "ATT":
            f.write("%0.3f %f %f %f\n" % (d['mileage'],d['lat'], d['lon'], d['acc_z']))
