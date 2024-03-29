#!/usr/bin/env python3
import json
import sys
import geo
import gps_to_mileage
import datetime

import pirail

if len(sys.argv) != 3:
    print("USAGE: %s data_file known_file" % sys.argv[0])
    sys.exit(1)

GPS_THRESHOLD = 0

GPS = gps_to_mileage.Gps2Miles(sys.argv[2])

acclist = []
data = []
last_tpv = None
used = count = 0
with open(sys.argv[1]) as f:
    for line in f:
        items = line.split()
        if items[-1] != "*":
            continue
        if items[1] == "L":
            obj = {
                'scan': eval(items[2]),
                'time': items[0],
                'class': 'LIDAR',
                'device': 'A1M8', 
            }
            acclist.append(obj)
        elif items[1] == "SKY":
            obj = json.loads(" ".join(items[2:-1]))
            acclist.append(obj)
            used = 0
            count = len(obj['satellites'])
            for s in obj['satellites']:
                if s['used']:
                    used += 1
            print("%d/%d" % (used,count))
            data.append(obj)
        elif items[1] == "LIDAR":
            obj = json.loads(" ".join(items[2:-1]))
            acclist.append(obj)
        elif items[1] == "WAV":
            obj = json.loads(" ".join(items[2:-1]))
            obj['time'] = items[0] 
            acclist.append(obj)
        elif items[1] == "TPV" and used >= GPS_THRESHOLD:
            obj = json.loads(" ".join(items[2:-1]))
            if obj['mode'] < 3:
                continue
            print(obj)
            if last_tpv is not None:
                if len(acclist) > 0:
                    delta_lat = (obj['lat'] - last_tpv['lat'])
                    delta_lon = (obj['lon'] - last_tpv['lon'])
                    delta_alt = (obj['alt'] - last_tpv['alt'])
                    for acc in acclist:
                        try:
                            millsec = float("0." + acc['time'].split(".")[1].replace("Z", ""))
                        except IndexError:
                            millsec = 0

                        acc['lat'] = last_tpv['lat'] + millsec*delta_lat
                        acc['lon'] = last_tpv['lon'] + millsec*delta_lon
                        acc['alt'] = last_tpv['alt'] + millsec*delta_alt
                        acc['mileage'], acc['certainty'] = GPS.find_mileage(acc['lat'], acc['lon'])
                        data.append(acc)
            obj['mileage'], obj['certainty'] = GPS.find_mileage(obj['lat'], obj['lon'])
            data.append(obj)
            if 'speed' in obj:
                y_speed = obj['speed']
            #if 'mileage' in obj:
            #    mileage = obj['mileage']
            if 'time' in obj:
                last_time = pirail.parse_time(obj['time'])
            if 'track' in obj:
                z_bearing = obj['track']
            if 'lat' in obj:
                latitude = obj['lat']
            if 'lon' in obj:
                longitude = obj['lon']
            if 'alt' in obj:
                altitude = obj['alt']

            last_tpv = obj
            acclist = []
        elif items[1] == "ATT":
            att = json.loads(" ".join(items[2:-1]))
            acclist.append(att)

print("Leftover elements = %d" % len(acclist))

for obj in acclist:
    if obj['class'] == "ATT":
        current = pirail.parse_time(obj['time'])
        DT = (current - last_time).total_seconds()

        y_speed += -obj['acc_y'] * DT
        z_bearing += obj['gyro_z'] * DT
        while z_bearing > 360:
            z_bearing -= 360
        while z_bearing < 0:
            z_bearing += 360
        #mileage += y_speed * DT
        latitude, longitude = geo.new_position(
            latitude,
            longitude,
            y_speed * DT,
            z_bearing,
        )
        last_time = current

    #obj['mileage'] = mileage
    #obj['certainty'] = 0
    obj['lat'] = latitude
    obj['lon'] = longitude
    obj['alt'] = altitude
    obj['mileage'], obj['certainty'] = GPS.find_mileage(obj['lat'], obj['lon'])
    data.append(obj)

# Sort By
#sortby='mileage'
SORTBY='time'
if SORTBY != 'time':
    data = sorted(data, key=lambda k: k[SORTBY], reverse=False)

with open("with_mileage_sortby_%s.json" % SORTBY, "w") as f:
    for obj in data:
        f.write(json.dumps(obj)+"\n")

new_data = []
accset = []
current = 0
step = 0.001
start_mileage = round(data[0]['mileage'],2)
next_mileage = start_mileage + step
while current < len(data):
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
