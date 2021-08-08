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
WIDTH=500
HEIGHT=700
SCALE=10.0 # mm per pixel

# Where to center the data
LIDAR_X = WIDTH / 2
LIDAR_Y = .8 * HEIGHT
LIDAR_RADIUS = .4 * WIDTH
#LIDAR_HEIGHT = 381.0 # mm above rail
LIDAR_HEIGHT = (304 + 352) / 2
LIDAR_OFFSET = (-944 + 390) / 2


DIRECTION=-1        # -1=backwards, 1=forwards
TOTAL_SLOPE = TOTAL_SLOPE_COUNT = TOTAL_GAUGE = TOTAL_GAUGE_COUNT = 0

MIN_SPEED = 0.5
SLOPE_THRESHOLD = 5 # Degrees

GHOST = 3 # slices

# Default Error Transformation
GAUGE_OFFSET = 1
ANGLE_OFFSET = 0
# Custom
ANGLE_OFFSET = 2.24
GAUGE_OFFSET = 1.16


# Colors
COLORS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "grey": (128, 128, 128),
    "black": (0, 0, 0),
}

def to_mph(speed):
    return speed * 2.23694 # convert to mph

def cvt_point(point):
    return (int(LIDAR_X - DIRECTION*(point[0] / SCALE)),
            int(LIDAR_Y - (point[1] / SCALE)))

# Front Mount
#LOW_RANGE = range(115, 111, -1)
#HIGH_RANGE = range(239, 243)
# Rear Mount
#LOW_RANGE = range(123, 119, -1)
#HIGH_RANGE = range(238, 242)
LOW_CENTER = 128
HIGH_CENTER = 249
DELTA = 2
LOW_RANGE = range(LOW_CENTER + DELTA, LOW_CENTER - DELTA, -1)
HIGH_RANGE = range(HIGH_CENTER - DELTA, HIGH_CENTER + DELTA)

def calc_gauge(data):
    min_dist_left = min_dist_right = 999999
    min_dist_left_i = min_dist_right_i = -1
    for i in LOW_RANGE:
        if data[i][0] <= min_dist_left and data[i][0] > 0:
            min_dist_left = data[i][0]
            min_dist_left_i = i
    for i in HIGH_RANGE:
        if data[i][0] <= min_dist_right and data[i][0] > 0:
            min_dist_right = data[i][0]
            min_dist_right_i = i

    if min_dist_right_i == -1 or min_dist_left_i == -1:
        return (0, 0, (0, 0), (0, 0))

    p1 = (data[min_dist_left_i][1], data[min_dist_left_i][2])
    p2 = (data[min_dist_right_i][1], data[min_dist_right_i][2])

    x = p1[0] - p2[0]
    y = p1[1] - p2[1]
    z = GAUGE_OFFSET * math.sqrt(x*x + y*y) / 25.4  # Convert to inches

    slope = math.degrees(math.atan(y / x))

    #if 56 < z < 57:
    #    print("A %d %d" % (min_dist_left_i, min_dist_right_i))

    return (z, slope, p1,p2)

def score_points(point, box):
    score = 0
    (px,py) = point
    (min_x, min_y, max_x, max_y) = box

    if min_x < px and px < max_x and min_y < py and py < max_y:
        score = 1
    else:
        score = 0

    return score


def plot(data, timestamp, latitude, longitude, mileage, speed, slice_count):
    global TOTAL_SLOPE, TOTAL_SLOPE_COUNT, TOTAL_GAUGE, TOTAL_GAUGE_COUNT

    labels = latitude != 0 and longitude != 0

    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(image)

    # Draw the LIDAR reference
    template_color = COLORS['blue']
    draw.ellipse((int(LIDAR_X-LIDAR_RADIUS),int(LIDAR_Y-LIDAR_RADIUS),int(LIDAR_X+LIDAR_RADIUS),int(LIDAR_Y+LIDAR_RADIUS)), outline=template_color)
    draw.line((0,int(LIDAR_Y),WIDTH,int(LIDAR_Y)),fill=template_color)
    draw.line((int(LIDAR_X),0,int(LIDAR_X),HEIGHT),fill=template_color)
    draw.text((int(LIDAR_X),int(LIDAR_Y-LIDAR_RADIUS)), "0", fill=template_color)
    draw.text((int(WIDTH-20),int(LIDAR_Y)), "90", fill=template_color)
    draw.text((0,int(LIDAR_Y)), "270", fill=template_color)
    draw.text((int(LIDAR_X),int(HEIGHT-10)), "180", fill=template_color)

    # Clearance Plate
    width = int(aar_plate.width / (2 * SCALE))
    height = int(aar_plate.height / SCALE)
    x_margin = int(width * 0.05)
    y_margin = int(height * 0.05)

    min_x = LIDAR_X-LIDAR_OFFSET-width
    max_x = LIDAR_X-LIDAR_OFFSET+width
    max_y = LIDAR_Y+LIDAR_HEIGHT/SCALE
    min_y = LIDAR_Y+LIDAR_HEIGHT/SCALE-height

    min_x_margin = min_x + x_margin
    max_x_margin = max_x - x_margin
    min_y_margin = min_y + y_margin
    max_y_margin = max_y - y_margin

    mid_y = (min_y + max_y) / 2

    # TC Outline
    width = int(1545.4 / (2 * SCALE))
    height = int(1676.4 / SCALE)
    min_tc_x = LIDAR_X-LIDAR_OFFSET-width
    max_tc_x = LIDAR_X-LIDAR_OFFSET+width
    max_tc_y = LIDAR_Y+LIDAR_HEIGHT/SCALE
    min_tc_y = LIDAR_Y+LIDAR_HEIGHT/SCALE-height

    # Draw Data
    new_data = [(0,0,0)] * len(data)
    plate_error = gauge_error = False
    score = 0
    for angle in range(0,len(data)):
        adjusted_angle = math.radians(angle+ANGLE_OFFSET)
        distance = data[angle]
        x = distance * math.sin(adjusted_angle)
        y = distance * math.cos(adjusted_angle)
        new_data[angle] = (distance, x, y)

        # Convert to image coordinates
        (px, py) = cvt_point((x, y))

        # ignore trackcar points
        if min_tc_x <= px <= max_tc_x and min_tc_y <= py <= max_tc_y:
            continue

        this_score = score_points((px,py), (min_x, min_y, max_x, max_y))
        this_score += score_points((px,py), (min_x_margin, min_y_margin, max_x_margin, max_y_margin))
        this_score += score_points((px,py), (min_x_margin, min_y_margin, max_x_margin, mid_y))
        score += this_score

        if this_score > 0:
            pc = COLORS['red']
            plate_error = True
            # Draw an X
            draw.line((px-5,py-5,px+5,py+5), fill=pc)
            draw.line((px+5,py-5,px-5,py+5), fill=pc)
        elif ((px <= min_x or px >= max_x) and py < max_y) or py < min_y:
            pc = COLORS['green']
            # Draw Circle
            draw.ellipse((px-5,py-5,px+5,py+5), outline=pc)
        else:
            pc = COLORS['black']
        draw.point((px, py), fill=pc)

    # Trackcar
    color_trackcar = COLORS['grey']
    draw.line((min_tc_x,max_tc_y,max_tc_x,max_tc_y), fill=color_trackcar)
    draw.line((min_tc_x,min_tc_y,max_tc_x,min_tc_y), fill=color_trackcar)
    draw.line((min_tc_x,max_tc_y,min_tc_x,min_tc_y), fill=color_trackcar)
    draw.line((max_tc_x,max_tc_y,max_tc_x,min_tc_y), fill=color_trackcar)
    draw.text((min_tc_x+5,min_tc_y+5), "Trackcar", fill=color_trackcar)

    # Draw the clearance box
    if not plate_error:
        color_plate = COLORS['green']
    else:
        color_plate = COLORS['red']
        draw.text((min_x+5,min_y+15), "Score = %d" % score, fill=color_plate)

    draw.line((min_x,max_y,max_x,max_y), fill=color_plate)
    draw.line((min_x,min_y,max_x,min_y), fill=color_plate)
    draw.line((min_x,max_y,min_x,min_y), fill=color_plate)
    draw.line((max_x,max_y,max_x,min_y), fill=color_plate)
    draw.text((min_x+5,min_y+5), aar_plate.full_name, fill=color_plate)

    # Calculate Gage
    gauge,slope,p1,p2 = calc_gauge(new_data)

    TOTAL_SLOPE += slope
    TOTAL_SLOPE_COUNT += 1
    TOTAL_GAUGE += gauge
    TOTAL_GAUGE_COUNT += 1

    p1 = cvt_point(p1)
    p2 = cvt_point(p2)

    if fra_class.min_gauge <= gauge <= fra_class.max_gauge:
        gauge_c = COLORS['black']
        if labels:
            draw.text((5,55), "GAGE: %0.2f in" % gauge, fill=gauge_c)
    #elif gauge < fra_class.min_gauge-1 or gauge > fra_class.max_gauge+1:
  #      gauge_c = COLORS['black']
  #      draw.text((5,55), "GAGE: *ERROR*", fill=gauge_c)
    elif gauge == 0:
        gauge_c = COLORS['black']
        if labels:
            draw.text((5,55), "GAGE: *ERROR*", fill=gauge_c)
    else:
        gauge_c = COLORS['red']
        gauge_error = True
        if labels:
            draw.line((p1,p2), fill=gauge_c)
            draw.text((5,55), "GAGE: %0.2f in" % gauge, fill=gauge_c)

    if labels:
        label_color = COLORS['black']
        draw.text((5,5), "UTC: %s" % timestamp, fill=label_color)
        draw.text((5,15), "LAT: %0.6f" % latitude, fill=label_color)
        draw.text((5,25), "LONG: %0.6f" % longitude, fill=label_color)
        draw.text((5,35), "MILEAGE: %0.2f" % mileage, fill=label_color)
        if speed < 10:
            draw.text((5,45), "SPEED: %0.1f mph" % speed, fill=label_color)
        else:
            draw.text((5,45), "SPEED: %d mph" % int(speed), fill=label_color)

    if OUTPUT:
        image.save("slices/slice_%08d.png" % slice_count)

    return {
        'gauge_error': gauge_error,
        'plate_error': plate_error,
        'gauge': gauge,
        'plate_score': score,
        'slope': slope,
    }

def clearance(filename):
    data = [99999]*360
    print(data)
    latitude = longitude = mileage = speed = 0
    for line_no,obj in pirail.read(filename, classes=['TPV', 'LIDAR']):
        if obj['class'] == "LIDAR":
            timestamp = obj['time']
            for angle, distance in obj['scan']:
                distance = lidar_util.estimate_from_lidar(float(distance))
                if distance > 1000 and speed > .5:
                    i = round(float(angle)) % 360
                    data[i] = min(data[i], float(distance))
        elif obj['class'] == "TPV":
            if 'speed' in obj:
                speed = to_mph(obj['speed'])

    report = plot(data, timestamp, latitude, longitude, mileage, speed, 0)
    print(report)

def main(filename):
    last_lat = last_lon = speed = 0
    slice_count = 0
    data = [0] * 360
    output = filename.replace("json", "kml")
    with open(output, "w") as k:
        k.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        k.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        k.write('<Document>\n')
        for line_no,obj in pirail.read(filename, classes=['TPV', 'LIDAR']):
            count = 0
            if obj['class'] == "TPV" and 'speed' in obj:
                speed = obj['speed']
            elif obj['class'] == "LIDAR" and speed >= MIN_SPEED:
                data = [0]*360
                for angle, distance in obj['scan']:
                    distance = lidar_util.estimate_from_lidar(float(distance))
                    i = round(float(angle)) % 360
                    data[i] = distance

                    report = plot(data, obj['time'], obj['lat'], obj['lon'], obj['mileage'], speed, slice_count)

                if report['gauge_error'] or report['plate_error']:
                    count += 1
                    if OUTPUT:
                        if (last_lat != obj['lat'] or last_lon != obj['lon']) and count > 10:
                            print("%d %0.6f %0.6f %0.6f %0.2f %d" % (slice_count, obj['lat'], obj['lon'], obj['mileage'], report['gauge'], report['plate_score']))
                            k.write('<Placemark>\n')
                            k.write('<name>Point %d</name>\n' % slice_count)
                            k.write('<description>\n')
                            k.write('Mileage = %0.2f\n' % obj['mileage'])
                            if report['gauge_error']:
                                k.write('Gage = %0.f in\n' % report['gauge'])
                            if report['plate_error']:
                                k.write(aar_plate.full_name + ' obstruction')
                            k.write('</description>\n')
                            k.write('<Point>\n')
                            k.write('<coordinates>%0.6f,%0.6f,%0.6f</coordinates>\n' % (obj['lon'],obj['lat'],obj['alt']))
                            k.write('</Point>\n')
                            k.write('</Placemark>\n')
                        last_lat = obj['lat']
                        last_lon = obj['lon']
                else:
                    count = 0
                slice_count += 1

        k.write('</Document>\n')
        k.write('</kml>\n')


#OUTPUT=True
#clearance(sys.argv[1])
#sys.exit(0)

try:
    datafile = sys.argv[-1]
except:
    print("USAGE: %s [args] data_file.json" % sys.argv[0])
    sys.exit(1)

if ANGLE_OFFSET == 0:
    print("Calculating Angle Offset...")
    OUTPUT = False
    main(datafile)
    try:
        ANGLE_OFFSET = TOTAL_SLOPE/TOTAL_SLOPE_COUNT
        GAUGE_OFFSET = 56.5/(TOTAL_GAUGE/TOTAL_GAUGE_COUNT)
    except ZeroDivisionError:
        ANGLE_OFFSET = 0
        GAUGE_OFFSET = 1

print("Generating Images...")
OUTPUT = True
TOTAL_SLOPE = TOTAL_SLOPE_COUNT = TOTAL_GAUGE = TOTAL_GAUGE_COUNT = 0
main(datafile)
print("ANGLE_OFFSET = %0.2f" % ANGLE_OFFSET)
print("GAUGE_OFFSET = %0.2f" % GAUGE_OFFSET)
