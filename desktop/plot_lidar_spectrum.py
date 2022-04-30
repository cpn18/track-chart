#!/usr/bin/env python3
import sys
import math
import json
from PIL import Image, ImageDraw, ImageOps
import plate_c as aar_plate
import class_i as fra_class
import lidar_a1m8 as lidar_util

import pirail

# Image Size
WIDTH=120
HEIGHT=360

MIN_SPEED=1

LIMIT=6000.0

def plot(x, data):
    global MAX
    for angle in range(0,len(data)):
        if data[angle] > LIMIT:
            color = 0
        else:
            color = 256 - int(256.0 * float(data[angle]) / LIMIT)
        y = angle
        draw.point((x, y), fill=(color, color, color))

def main(filename):
    x = 0
    data = [0]*360
    for line_no,obj in pirail.read(filename, classes=['TPV', 'LIDAR']):
        count = 0
        if obj['class'] == "TPV" and 'speed' in obj:
            speed = obj['speed']
        elif obj['class'] == "LIDAR" and speed >= MIN_SPEED:
            for angle, distance in obj['scan']:
                distance = lidar_util.estimate_from_lidar(float(distance))
                i = round(float(angle)) % 360
                data[i] = distance

            plot(x, data)
            x += 1
            if x == WIDTH:
                break

try:
    datafile = sys.argv[-1]
except:
    print("USAGE: %s [args] data_file.json" % sys.argv[0])
    sys.exit(1)

image = Image.new("RGB", (WIDTH, HEIGHT), "white")
draw = ImageDraw.Draw(image)
main(datafile)
image.save("spectrum.png")
