#!/usr/bin/env python3
"""
Useful when debugging GPS issues
"""
import sys
import math
import statistics
import json

import pirail

aax = -0.76994928407068
aay = -0.12089123215864023
aaz = 9.789026816711136
agx = -4.4119982547992525
agy = -2.77166666666651
agz = -0.5585602094240765

def main(filename):
    sums = {
        'acc_x': 0,
        'acc_y': 0,
        'acc_z': 0,
        'gyro_x': 0,
        'gyro_y': 0,
        'gyro_z': 0,
    }
    cnt = 0
    print("Time ax ay az gx gy gz")
    for line_no, obj in pirail.read(filename, classes=['ATT']):
        print("%s %f %f %f %f %f %f" % (
            obj['time'],
            obj['acc_x'] - aax, obj['acc_y'] - aay, obj['acc_z'] - aaz,
            obj['gyro_x'] - agx, obj['gyro_y'] - agy, obj['gyro_z'] - agz,
        ))
        sums['acc_x'] += obj['acc_x']
        sums['acc_y'] += obj['acc_y']
        sums['acc_z'] += obj['acc_z']
        sums['gyro_x'] += obj['gyro_x']
        sums['gyro_y'] += obj['gyro_y']
        sums['gyro_z'] += obj['gyro_z']
        cnt += 1
    print("Average %f %f %f %f %f %f" % (
        sums['acc_x']/cnt, sums['acc_y']/cnt, sums['acc_z']/cnt,
        sums['gyro_x']/cnt, sums['gyro_y']/cnt, sums['gyro_z']/cnt,
    ))

if len(sys.argv) < 2:
    print("USAGE: %s [args] data_file.json" % sys.argv[0])
    sys.exit(1)

main(sys.argv[-1])
