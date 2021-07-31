#!/usr/bin/env python
import sys
import datetime
import json
import math

import pirail

# Based on:
# https://github.com/ozzmaker/BerryIMU/blob/master/python-BerryIMU-gryo-accel-compass/berryIMU-simple.py

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
AA = 0.40 # Complementary filter constant

data=[]
with open(sys.argv[1]) as f:
    for line in f:
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

gyroXangle = gyroYangle = gyroZangle = CFangleX = CFangleY = CFangleZ = 0

print("Time", "Lat", "Long", "AngleX", "AngleY", "AngleZ")
last_time = data[0]['time']
for obj in data:
    DT = (pirail.parse_time(obj['time']) - pirail.parse_time(last_time)).total_seconds()

    gyroXangle+=obj['gyro_x']*DT;
    gyroYangle+=obj['gyro_y']*DT;
    gyroZangle+=obj['gyro_z']*DT;

    AccXangle = (float) (math.atan2(obj['acc_y'],obj['acc_z'])+M_PI)*RAD_TO_DEG;
    AccYangle = (float) (math.atan2(obj['acc_z'],obj['acc_x'])+M_PI)*RAD_TO_DEG;
    AccZangle = (float) (math.atan2(obj['acc_y'],obj['acc_x'])+M_PI)*RAD_TO_DEG;

    # Complementary Filter
    CFangleX=AA*(CFangleX+obj['gyro_x']*DT) +(1 - AA) * AccXangle;
    CFangleY=AA*(CFangleY+obj['gyro_y']*DT) +(1 - AA) * AccYangle;
    CFangleZ=AA*(CFangleZ+obj['gyro_z']*DT) +(1 - AA) * AccZangle;

    print(obj['time'], obj['lat'], obj['lon'], CFangleX, CFangleY, CFangleZ)
    last_time = obj['time']
