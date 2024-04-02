#!/usr/bin/env python3
import sys
import math
import json
import base64
import matplotlib.pyplot as plt

import pirail
import spectrum

# Image Size
WIDTH=160
HEIGHT=60
SCALE=2

MIN_SPEED = -10.0

LIMIT = 2000

GREYSCALE = False

LENS = False

def invalid_depth(depth):
    return depth in [0x0000, 0xFF14, 0xFF78, 0xFFDC, 0xFFFA]

def near(a, b, delta=10):
    return abs(a-b) <= delta

def minmax(data):
    WIDTH = len(data[0])
    HEIGHT = len(data)
    mind = [0] * WIDTH
    maxd = [0] * WIDTH
    for x in range(WIDTH):
        mind[x] = 999999
        maxd[x] = 0
        for y in range(HEIGHT):
            if invalid_depth(data[y][x]):
                continue

            depth = data[y][x]

            mind[x] = min(mind[x], depth)
            maxd[x] = max(maxd[x], depth)

    return (mind, maxd)

def sph2cart(azimuth, elevation, radius):
    el = math.radians(90-elevation)
    az = math.radians(90+azimuth)
    cos_el = math.cos(el)
    x = radius * cos_el * math.cos(az)
    y = radius * cos_el * math.sin(az)
    z = radius * math.sin(el)
    return x, y, z

def scatterplot(data):

    WIDTH = len(data[0])
    HEIGHT = len(data)
    HFOV = 76.0 # degrees
    VFOV = 32.0 # degrees

    print(WIDTH,HEIGHT)

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    minD = 99999
    maxD = 0
    for c in range(int(WIDTH)):
        for r in range(int(HEIGHT)):
            depth = data[r][c]
            if invalid_depth(depth):
                continue
            #if depth > LIMIT:
            #    continue
            minD = min(minD,depth)
            maxD = max(maxD,depth)

    for c in range(int(WIDTH)):
        if c % 2 == 1:
            continue
        for r in range(int(HEIGHT)):
            if r % 2 == 1:
                continue

            depth = min(data[r][c], data[r][c+1], data[r+1][c+1],data[r+1][c])

            if invalid_depth(depth):
                continue

            if depth > LIMIT:
                continue

            az = c * HFOV/WIDTH - HFOV/2
            el = VFOV/2 - r*VFOV/HEIGHT

            if LENS:
                x, z, y = sph2cart(az, el, depth)
            else:
                x = c - WIDTH/2
                z = HEIGHT/2 - r
                y = depth

            ci = int((len(spectrum.SPECTRUM)-1) * (float(depth) - minD) / (maxD - minD))
            color = spectrum.SPECTRUM[ci]

            color = (color[0]/255, color[1]/255, color[2]/255)
            ax.scatter(
                    -x, y, z,
                marker='.',
                color=color
            )

    #ax.scatter(
    #    -WIDTH/2, 100, HEIGHT/2,
    #    marker='o',
    #    color="#0000FF"
    #)
    #ax.scatter(
    #    WIDTH/2, 100, HEIGHT/2,
    #    marker='o',
    #    color="#00FF00"
    #)
    #ax.scatter(
    #    -WIDTH/2, 100, -HEIGHT/2,
    #    marker='o',
    #    color="#00FF00"
    #)
    #ax.scatter(
    #    WIDTH/2, 100, -HEIGHT/2,
    #    marker='o',
    #    color="#00FF00"
    #)
    ax.scatter(
        0, 0, 0,
        marker='o',
        color="#000000"
    )

    ax.set_xlabel('x')
    ax.set_ylabel('z')
    ax.set_zlabel('y')

    plt.show()


def main(filename, data_frame_counter):
    last_lat = last_lon = speed = 0
    slice_count = 0

    for line_no,obj in pirail.read(filename, classes=['TPV', 'LIDAR3D']):
        count = 0
        if obj['class'] == "TPV" and 'speed' in obj:
            speed = obj['speed']
        elif obj['class'] == "LIDAR3D" and speed >= MIN_SPEED:
            if 'depth' not in obj:
                continue
            if obj['data_frame_counter'] != data_frame_counter:
                continue

            report = scatterplot(obj['depth'])
            break

try:
    data_frame_counter = int(sys.argv[-2])
    datafile = sys.argv[-1]
except:
    print("USAGE: %s [args] data_frame_counter data_file.json" % sys.argv[0])
    sys.exit(1)

main(datafile, data_frame_counter)
