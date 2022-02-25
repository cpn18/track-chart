#!/usr/bin/env python3
"""
Convert CSV file to JSON
"""
import json
import sys
import datetime
import math

import pirail

AA = 0.03 # Complementary filter constant

if len(sys.argv) < 2:
    print("USAGE: %s [args] data_file" % sys.argv[0])
    sys.exit(1)
else:
    data_file = sys.argv[-1]

data = []
with open(data_file) as f:
    for line in f:
        line = line.replace("'", '"')
        line = line.replace("True", "true")
        items = line.split()
        if items[-1] != "*":
            continue
        print(" ".join(items[2:-1]))
        try:
            obj = json.loads(" ".join(items[2:-1]))
        except json.decoder.JSONDecodeError:
            # Ignore data that fails to parse JSON
            continue

        # Add fields if not present
        if not 'class' in obj:
            obj['class'] = 'DEBUG'
        if not 'time' in obj:
            obj['time'] = items[0]

        data.append(obj)

SORTBY='time'
if SORTBY != 'time':
    data = sorted(data, key=lambda k: k[SORTBY], reverse=False)

# Add num_sat and num_used
num_sat = num_used = 0
for obj in data:
    if obj['class'] == "SKY":
        num_sat = num_used = 0
        for s in obj['satellites']:
            num_sat += 1
            if s['used']:
                num_used += 1
    elif obj['class'] == "TPV" and not 'num_used' in obj:
        obj['num_sat'] = num_sat
        obj['num_used'] = num_used

# Calculate Yaw/Pitch/Roll
# Based on:
# https://github.com/ozzmaker/BerryIMU/blob/master/python-BerryIMU-gryo-accel-compass/berryIMU-simple.py
CFangleX = CFangleY = CFangleZ = 0
gyroXangle = gyroYangle = gyroZangle = 0
last_time = None
for obj in data:
    # Skip over non-IMU data
    if obj['class'] != "ATT":
        continue

    # Time Delta
    if last_time is not None:
        DT = (pirail.parse_time(obj['time']) - pirail.parse_time(last_time)).total_seconds()
    else:
        DT = 0
    last_time = obj['time']

    # Calculate the angles from the gyro
    gyroXangle+=obj['gyro_x']*DT
    gyroYangle+=obj['gyro_y']*DT
    gyroZangle+=obj['gyro_z']*DT
    gyroXangle = gyroXangle % 360
    gyroYangle = gyroYangle % 360
    gyroZangle = gyroZangle % 360
    # Complementary Filter
    AccXangle = math.degrees(math.atan2(obj['acc_y'], obj['acc_z']) + math.pi)
    AccYangle = math.degrees(math.atan2(obj['acc_z'], obj['acc_x']) + math.pi)
    AccZangle = math.degrees(math.atan2(obj['acc_y'], obj['acc_x']) + math.pi)
    CFangleX = AA * (CFangleX + obj['gyro_x'] * DT) + (1 - AA) * AccXangle
    CFangleY = AA * (CFangleY + obj['gyro_y'] * DT) + (1 - AA) * AccYangle
    CFangleZ = AA * (CFangleZ + obj['gyro_z'] * DT) + (1 - AA) * AccZangle

    if 'roll' in obj:
        CFangleY = obj['roll']
    else:
        obj['roll'] = CFangleY

    if 'pitch' in obj:
        CFangleX = obj['pitch']
    else:
        obj['pitch'] = CFangleX

    if 'yaw' in obj:
        CFangleZ = obj['yaw']
    else:
        obj['yaw'] = CFangleZ

    obj['gyro_x_angle'] = gyroXangle
    obj['gyro_y_angle'] = gyroYangle
    obj['gyro_z_angle'] = gyroZangle

# Normalize yaw/pitch/roll
#count = sum_roll = sum_pitch = sum_yaw = 0
#for obj in data:
#    if 'roll' in obj:
#        sum_roll += obj['roll']
#        sum_pitch += obj['pitch']
#        sum_yaw += obj['yaw']
#        count += 1
#avg_roll = sum_roll / count
#avg_pitch = sum_pitch / count
#avg_yaw = sum_yaw / count
#for obj in data:
#    if 'roll' in obj:
#        obj['roll'] -= avg_roll
#        obj['pitch'] -= avg_pitch
#        obj['yaw'] -= avg_yaw

with open(data_file.replace('.csv', '.json'), "w") as f:
    for obj in data:
        f.write(json.dumps(obj)+"\n")
