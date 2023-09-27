#!/usr/bin/env python3
import sys
import math
import json
import base64
from PIL import Image, ImageDraw, ImageOps

import pirail
import spectrum

# Image Size
WIDTH=160
HEIGHT=60
SCALE=2

MIN_SPEED = -10.0

GREYSCALE = False

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

def plot(data, slice_count):

    WIDTH = len(data[0])
    HEIGHT = len(data)

    image = Image.new("RGB", (SCALE*WIDTH, SCALE*HEIGHT), "black")
    draw = ImageDraw.Draw(image)

    mind, maxd = minmax(data)

    min_d = 9999999
    max_d = 0
    sum_d = 0
    cnt_d = 0
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if invalid_depth(data[y][x]):
                continue
            depth = float(data[y][x])
            min_d = min(min_d, depth)
            max_d = max(max_d, depth)
            sum_d += depth
            cnt_d += 1

    for x in range(WIDTH):
        for y in range(HEIGHT):

            depth = data[y][x]

            xr = SCALE*x
            yr = SCALE*y

            if invalid_depth(depth):
                if depth in [65400, 65500]:
                    color = spectrum.WHITE
                else:
                    color = spectrum.BLACK
            elif not GREYSCALE:
                if max_d == min_d:
                    # Protect Against Divide by Zero
                    color = spectrum.WHITE
                else:
                    c = int((len(spectrum.SPECTRUM)-1) * (float(depth) - min_d) / (max_d - min_d))
                    color = spectrum.SPECTRUM[c]
            else:
                if near(depth, mind[x]):
                    color = spectrum.RED
                elif near(depth, maxd[x]):
                    color = spectrum.GREEN
                else:
                    c = 255 - int(255.0 * (float(depth) - min_d) / (max_d - min_d))
                    color = (c,c,c)

            draw.point((xr, yr), color)

    image.save("slices/slice_%08d.png" % slice_count)

def main(filename):
    last_lat = last_lon = speed = 0
    slice_count = 0

    for line_no,obj in pirail.read(filename, classes=['TPV', 'LIDAR3D']):
        count = 0
        if obj['class'] == "TPV" and 'speed' in obj:
            speed = obj['speed']
        elif obj['class'] == "LIDAR3D" and speed >= MIN_SPEED:
            if 'depth' not in obj:
                continue

            if isinstance(obj['depth'], str):
                # Convert from Base64 to Array of Short Int
                raw_string = base64.b64decode(obj['depth'])
                depth = []
                index = 0
                for row in range(0, obj['rows']):
                    depth_row = []
                    for col in range(0, obj['columns']):
                        depth_row.append(raw_string[index] + raw_string[index+1] * 256)
                        index += 2
                    depth.append(depth_row)
                report = plot(depth, slice_count)

            else:
                # Legacy JSON array
                report = plot(obj['depth'], slice_count)

            slice_count += 1

try:
    datafile = sys.argv[-1]
except:
    print("USAGE: %s [args] data_file.json" % sys.argv[0])
    sys.exit(1)

main(datafile)
