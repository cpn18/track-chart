#!/usr/bin/env python
import sys
import datetime
import json
import math

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
AA = 0.40 # Complementary filter constant


def parse_time(time_string):
    return datetime.datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")

data=[]
with open(sys.argv[1]) as f:
    for line in f:
        try:
            items = line.split()
            if items[-1] != "*":
                continue
            if items[1] == "TPV":
                tpv = json.loads(" ".join(items[2:-1]))
            elif items[1] == "ATT":
                att = json.loads(" ".join(items[2:-1]))
                att['lat'] = tpv['lat']
                att['lon'] = tpv['lon']
                data.append(att)
                #data.append((items[0],
                    #obj['acc_x'],
                    #obj['acc_y'],
                    #obj['acc_z'],
                    #obj['gyro_x'],
                    #obj['gyro_y'],
                    #obj['gyro_z'],
                #))
        except:
            pass

print("Time", "Lat", "Long", "JerkY", "AccY", "SpeedY", "DistanceY")
last_time = data[0]['time']
last_accy = data[0]['acc_x']
speed = 0
distance = 0
for obj in data:
    DT = (parse_time(obj['time']) - parse_time(last_time)).total_seconds()

    if DT == 0:
        jerky = 0
    else:
        jerky = (obj['acc_x'] - last_accy) / DT

    speed += obj['acc_x'] * DT

    distance += speed * DT

    print(obj['time'], obj['lat'], obj['lon'], jerky, obj['acc_x'], speed, distance)
    last_time = obj['time']
    last_accy = obj['acc_x']
