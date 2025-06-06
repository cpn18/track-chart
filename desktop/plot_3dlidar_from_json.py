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

def plot(data, slice_count, mask=None):

    WIDTH = len(data[0])
    HEIGHT = len(data)

    box_x_min = 9999
    box_x_max = 0
    box_y_min = 9999
    box_y_max = 0

    if mask is not None:
        for point in mask:
            box_y_min = min(box_y_min, point[0])
            box_y_max = max(box_y_max, point[0])
            box_x_min = min(box_x_min, point[1])
            box_x_max = max(box_x_max, point[1])

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

            if False and mask is not None and (x,y) not in mask:
                color = spectrum.BLACK
            elif invalid_depth(depth):
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

    if mask is not None:
        draw.line((mask[-1][1], mask[-1][0],box_x_max,box_y_max), fill=spectrum.WHITE)
        draw.line((mask[-1][1], mask[-1][0],box_x_max,box_y_min), fill=spectrum.WHITE)
        draw.line((mask[-1][1], mask[-1][0],box_x_min,box_y_max), fill=spectrum.WHITE)
        draw.line((mask[-1][1], mask[-1][0],box_x_min,box_y_min), fill=spectrum.WHITE)
        draw.rectangle((box_x_min, box_y_min,box_x_max,box_y_max), outline=spectrum.WHITE)

    title = "%08d" % slice_count
    (x_size, y_size) = draw.textsize(title)
    draw.rectangle((0,0,x_size+2,y_size+2), fill=spectrum.WHITE)
    draw.text((1, 1), title, fill=spectrum.BLACK)

    image.save("slices/slice_%s.png" % title)

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

            report = plot(obj['depth'], obj['data_frame_counter'])

            slice_count += 1

if __name__ == "__main__":
    try:
        datafile = sys.argv[-1]
    except:
        print("USAGE: %s [args] data_file.json" % sys.argv[0])
        sys.exit(1)

    main(datafile)
