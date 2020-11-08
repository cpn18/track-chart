#!/usr/bin/env python3
import sys
import math
import json
import gps_to_mileage
from PIL import Image, ImageDraw, ImageOps
import plate_c as aar_plate
import class_i as fra_class

WIDTH=500
HEIGHT=700

LIDAR_X = WIDTH / 2
LIDAR_Y = .8 * HEIGHT 
LIDAR_RADIUS = .4 * WIDTH

SCALE=10

DIRECTION=-1        # -1=backwards, 1=forwards
ANGLE_OFFSET = 3.51
TOTAL_SLOPE = 0
TOTAL_SLOPE_COUNT = 0

MIN_SPEED = 0.5

GHOST = 3

ERROR=1
ERROR=.9511

def to_mph(speed):
    return speed * 2.23694 # convert to mph

def cvt_point(point):
    return (int(LIDAR_X - DIRECTION*(point[0] / SCALE)),
            int(LIDAR_Y - (point[1] / SCALE)))

# average 113.665, 241.342
#LOW_RANGE = range(120, 110, -1)
#HIGH_RANGE = range(240, 250)
# Front Mount
#LOW_RANGE = range(115, 111, -1)
#HIGH_RANGE = range(239, 243)
# Rear Mount
#LOW_RANGE = range(123, 119, -1)
#HIGH_RANGE = range(238, 242)
LOW_CENTER = 114
HIGH_CENTER = 240
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

    if min_dist_right_i == -1 or min_dist_left_i == 0:
        return (0, 0, (0, 0), (0, 0))

    p1 = (data[min_dist_left_i][1], data[min_dist_left_i][2])
    p2 = (data[min_dist_right_i][1], data[min_dist_right_i][2])

    x = p1[0] - p2[0]
    y = p1[1] - p2[1]
    z = (1/ERROR) * math.sqrt(x*x + y*y) / 25.4  # Convert to inches

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


def plot(data, timestamp, latitude, longitude, mileage, speed, slice):
    global TOTAL_SLOPE, TOTAL_SLOPE_COUNT

    if latitude != 0 and longitude != 0:
        labels = True
    else:
        labels = False

    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(image)
    draw.ellipse((int(LIDAR_X-LIDAR_RADIUS),int(LIDAR_Y-LIDAR_RADIUS),int(LIDAR_X+LIDAR_RADIUS),int(LIDAR_Y+LIDAR_RADIUS)), outline=(0,0,255))
    draw.line((0,int(LIDAR_Y),WIDTH,int(LIDAR_Y)),fill=(0,0,255))
    draw.line((int(LIDAR_X),0,int(LIDAR_X),HEIGHT),fill=(0,0,255))
    draw.text((int(LIDAR_X),int(LIDAR_Y-LIDAR_RADIUS)), "0", fill=(0,0,255))
    draw.text((int(WIDTH-20),int(LIDAR_Y)), "90", fill=(0,0,255))
    draw.text((0,int(LIDAR_Y)), "270", fill=(0,0,255))
    draw.text((int(LIDAR_X),int(HEIGHT-10)), "180", fill=(0,0,255))

    # Clearance Plate
    offset = 30 
    width = int(aar_plate.width / (2 * SCALE))
    height = int(aar_plate.height / SCALE)
    x_margin = int(width * 0.05)
    y_margin = int(height * 0.05) 

    min_x = LIDAR_X-width
    max_x = LIDAR_X+width
    max_y = LIDAR_Y+offset
    min_y = LIDAR_Y+offset-height

    min_x_margin = min_x + x_margin
    max_x_margin = max_x - x_margin
    min_y_margin = min_y + y_margin
    max_y_margin = max_y - y_margin

    mid_y = (min_y + max_y) / 2

    # TC Outline
    width = int(1545.4 / (2 * SCALE))
    height = int(1676.4 / SCALE)
    min_tc_x = LIDAR_X-width
    max_tc_x = LIDAR_X+width
    max_tc_y = LIDAR_Y+offset
    min_tc_y = LIDAR_Y+offset-height
    
    # Draw Data
    new_data = [(0,0,0)] * len(data)
    plate_error = gauge_error = False
    score = 0
    for angle in range(0,len(data)):
        x = data[angle] * math.sin(math.radians(angle+ANGLE_OFFSET))
        y = data[angle] * math.cos(math.radians(angle+ANGLE_OFFSET))
        new_data[angle] = (data[angle], x, y)
        if data[angle] < 200:
            continue

        (px, py) = cvt_point((x, y))

        this_score = score_points((px,py), (min_x, min_y, max_x, max_y))
        this_score += score_points((px,py), (min_x_margin, min_y_margin, max_x_margin, max_y_margin))
        this_score += score_points((px,py), (min_x_margin, min_y_margin, max_x_margin, mid_y))
        score += this_score

        if this_score > 0:
            pc = (255, 0, 0)
            plate_error = True
            draw.line((px-5,py-5,px+5,py+5), fill=pc)
            draw.line((px+5,py-5,px-5,py+5), fill=pc)
        elif (px <= min_x or px >= max_x) and py < max_y:
            pc = (0, 255, 0)
            draw.ellipse((px-5,py-5,px+5,py+5), outline=pc)
        else:
            pc = (0, 0, 0)
        draw.point((px, py), fill=pc)
    
    # Trackcar
    plate_c=(128,128,128)
    draw.line((min_tc_x,max_tc_y,max_tc_x,max_tc_y), fill=plate_c)
    draw.line((min_tc_x,min_tc_y,max_tc_x,min_tc_y), fill=plate_c)
    draw.line((min_tc_x,max_tc_y,min_tc_x,min_tc_y), fill=plate_c)
    draw.line((max_tc_x,max_tc_y,max_tc_x,min_tc_y), fill=plate_c)
    draw.text((min_tc_x+5,min_tc_y+5), "Trackcar", fill=plate_c)

    # Draw the clearance box
    if plate_error:
        plate_c = (255,0,0)
        draw.text((min_x+5,min_y+15), "Score = %d" % score, fill=plate_c)
    else:
        plate_c = (0,255,0)
    draw.line((min_x,max_y,max_x,max_y), fill=plate_c)
    draw.line((min_x,min_y,max_x,min_y), fill=plate_c)
    draw.line((min_x,max_y,min_x,min_y), fill=plate_c)
    draw.line((max_x,max_y,max_x,min_y), fill=plate_c)
    draw.text((min_x+5,min_y+5), aar_plate.full_name, fill=plate_c)

    # Calculate Gage
    gauge,slope,p1,p2 = calc_gauge(new_data)

    TOTAL_SLOPE += slope
    TOTAL_SLOPE_COUNT += 1

    p1 = cvt_point(p1)
    p2 = cvt_point(p2)

    if fra_class.min_gauge <= gauge <= fra_class.max_gauge:
        gauge_c = (0,0,0)
        if labels:
            draw.text((5,55), "GAGE: %0.2f in" % gauge, fill=gauge_c)
    #elif gauge < fra_class.min_gauge-1 or gauge > fra_class.max_gauge+1:
  #      gauge_c = (0,0,0)
  #      draw.text((5,55), "GAGE: *ERROR*", fill=(255,0,0))
    elif gauge == 0:
        gauge_c = (0,0,0)
        if labels:
            draw.text((5,55), "GAGE: *ERROR*", fill=(255,0,0))
    else:
        gauge_c = (255,0,0)
        gauge_error = True
        if labels:
            draw.line((p1,p2), fill=gauge_c)
            draw.text((5,55), "GAGE: %0.2f in" % gauge, fill=gauge_c)

    if labels:
        draw.text((5,5), "UTC: %s" % timestamp, fill=(0,0,0))
        draw.text((5,15), "LAT: %0.6f" % latitude, fill=(0,0,0))
        draw.text((5,25), "LONG: %0.6f" % longitude, fill=(0,0,0))
        draw.text((5,35), "MILEAGE: %0.2f" % mileage, fill=(0,0,0))
        if speed < 10:
            draw.text((5,45), "SPEED: %0.1f mph" % speed, fill=(0,0,0))
        else:
            draw.text((5,45), "SPEED: %d mph" % int(speed), fill=(0,0,0))

    if OUTPUT:
        image.save("slices/slice_%08d.png" % slice)
    
    return {'gauge_error': gauge_error, 'plate_error': plate_error, 'gauge': gauge, 'plate_score': score}

def clearance(filename):
    data = [99999]*360
    print(data)
    latitude = longitude = mileage = speed = 0
    with open(filename, "r") as f:
        for line in f:
            if line[0] == "#" or line[-2] != "*":
                continue
            fields = line.split(" ")
            if fields[1] == "LIDAR":
                lidar = json.loads(" ".join(fields[2:-1]))
                timestamp = lidar['time']
                for angle, distance in lidar['scan']:
                    i = round(float(angle)) % 360
                    if distance > 1000 and speed > .5:
                        data[i] = min(data[i], float(distance))
            elif fields[1] == "L":
                timestamp, datatype, scan_data = line.split(" ", 2)
                scan_data = eval(scan_data.replace('*', ''))
                for angle, distance in scan_data:
                    i = round(float(angle)) % 360
                    if distance > 1000 and speed > .5:
                        data[i] = min(data[i], float(distance))
            elif fields[1] == "TPV":
                obj = json.loads(" ".join(fields[2:-1]))
                if 'speed' in obj:
                    speed = to_mph(obj['speed'])
                    print(speed)

    report = plot(data, timestamp, latitude, longitude, mileage, speed, 0)
    print(report)

def main(filename, known):
    G = gps_to_mileage.Gps2Miles(known)
    #G.sanity_check(update=True)
    last_lat = last_lon = speed = latitude = longitude = mileage = 0
    slice = 0
    data = [0] * 360
    ghost = [0] * 360
    with open(filename.split('.')[0]+".kml","w") as k:
        k.write('<xml version="1.0" encoding="UTF-8"?>\n')
        k.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        k.write('<Document>\n')
        with open(filename, "r") as f:
            count = 0
            for line in f:
                if line[0] == "#":
                    continue
                if line[-2] != "*":
                    continue
                fields = line.split(" ")
                if fields[1] == "A":
                    pass
                elif fields[1] == "TPV":
                    obj = json.loads(" ".join(fields[2:-1]))
                    try:
                        latitude = obj['lat']
                    except KeyError:
                        pass
                    try:
                        longitude = obj['lon']
                    except KeyError:
                        pass
                    try:
                        altitude = obj['alt']
                    except KeyError:
                        pass
                    try:
                        speed = to_mph(obj['speed'])
                    except KeyError:
                        pass
                    mileage, certainty = G.find_mileage(latitude, longitude)
                elif fields[1] == "G":
                    fields = line.split(' ')
                    try:
                        latitude = float(fields[2])
                    except ValueError:
                        pass
                    try:
                        longitude = float(fields[3])
                    except ValueError:
                        pass
                    try:
                        altitude = float(fields[4])
                    except ValueError:
                        pass
                    try:
                        speed = to_mph(float(fields[8]))
                    except ValueError:
                        pass
                    mileage, certainty = G.find_mileage(latitude, longitude)
                elif (fields[1] == "L" or fields[1] == "LIDAR") and speed >= MIN_SPEED:
                    #print(line)
                    if fields[1] == "LIDAR":
                        lidar = json.loads(" ".join(fields[2:-1]))
                        timestamp = lidar['time']
                        scan_data = lidar['scan']
                    else:
                        timestamp, datatype, scan_data = line.split(" ", 2)
                        scan_data = eval(scan_data.replace('*', ''))
                    data = [0]*360
                    for i in range(0,360):
                        ghost[i] -= 1
                        if ghost[i] == 0:
                            data[i] = 0
                    for angle, distance in scan_data:
                        i = round(float(angle)) % 360
                        data[i] = float(distance)
                        ghost[i] = GHOST

                    report = plot(data, timestamp, latitude, longitude, mileage, speed, slice)
                    if report['gauge_error'] or report['plate_error']:
                        count += 1
                        if OUTPUT:
                            if last_lat != latitude or last_lon != longitude:
                                print("%d %0.6f %0.6f %0.6f %0.2f %d" % (slice, latitude, longitude, mileage, report['gauge'], report['plate_score']))
                                k.write('<Placemark>\n')
                                k.write('<name>Point %d</name>\n' % slice)
                                k.write('<description>\n')
                                k.write('Mileage = %0.2f\n' % mileage)
                                if report['gauge_error']:
                                    k.write('Gage = %0.f in\n' % report['gauge'])
                                if report['plate_error']:
                                    k.write('Plate F obstruction')
                                k.write('</description>\n')
                                k.write('<Point>\n')
                                k.write('<coordinates>%0.6f,%0.6f,%0.6f</coordinates>\n' % (longitude,latitude,altitude))
                                k.write('</Point>\n')
                                k.write('</Placemark>\n')
                            last_lat = latitude
                            last_lon = longitude
                    else:
                        count = 0
                    slice += 1
                else:
                    ghost = [0] * 360
        k.write('</Document>\n')
        k.write('</kml>\n')

#OUTPUT=True
#clearance(sys.argv[1])
#sys.exit(0)

if ANGLE_OFFSET == 0:
    print("Calculating Angle Offset...")
    OUTPUT = False
    main(sys.argv[1], sys.argv[2])
    try:
       ANGLE_OFFSET = TOTAL_SLOPE/TOTAL_SLOPE_COUNT
    except ZeroDivisionError:
        ANGLE_OFFSET = 0

print("Angle Offset = %0.2f" % ANGLE_OFFSET)

print("Generating Images...")
OUTPUT = True
TOTAL_SLOPE = TOTAL_SLOPE_COUNT = 0
main(sys.argv[1], sys.argv[2])
