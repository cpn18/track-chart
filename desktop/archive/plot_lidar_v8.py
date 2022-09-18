#!/usr/bin/env python3
import sys
import math
import gps_to_mileage
from PIL import Image, ImageDraw, ImageOps

WIDTH=500
HEIGHT=700

LIDAR_X = WIDTH / 2
LIDAR_Y = .8 * HEIGHT 
LIDAR_RADIUS = .4 * WIDTH

SCALE=10

DIRECTION=-1
ANGLE_OFFSET = 0
TOTAL_SLOPE = 0
TOTAL_SLOPE_COUNT = 0

def calc_gauge(data):
    min_dist_left = min_dist_right = 999999
    min_dist_left_i = min_dist_right_i = -1
    for i in range(110, 115):
        if data[i][0] < min_dist_left and data[i][0] > 0:
            min_dist_left = data[i][0]
            min_dist_left_i = i
    for i in range(240, 245):
        if data[i][0] < min_dist_right and data[i][0] > 0:
            min_dist_right = data[i][0]
            min_dist_right_i = i

    if min_dist_right_i == -1 or min_dist_left_i == 0:
        return 0

    x = (data[min_dist_left_i][1] - data[min_dist_right_i][1])
    y = (data[min_dist_left_i][2] - data[min_dist_right_i][2])
    z = math.sqrt(x*x + y*y) / 25.4  # Convert to inches

    slope = math.degrees(math.atan(y / x))

    return (z, slope, min_dist_left_i, min_dist_right_i)

def plot(data, timestamp, latitude, longitude, mileage, speed, slice):
    global TOTAL_SLOPE, TOTAL_SLOPE_COUNT

    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(image)
    draw.ellipse((int(LIDAR_X-LIDAR_RADIUS),int(LIDAR_Y-LIDAR_RADIUS),int(LIDAR_X+LIDAR_RADIUS),int(LIDAR_Y+LIDAR_RADIUS)), outline=(0,0,255))
    draw.line((0,int(LIDAR_Y),WIDTH,int(LIDAR_Y)),fill=(0,0,255))
    draw.line((int(LIDAR_X),0,int(LIDAR_X),HEIGHT),fill=(0,0,255))

    # AAR Plate F
    offset = 30 
    width = int(3251.20 / (2 * SCALE))
    height = int(5181.60 / SCALE)

    min_x = LIDAR_X-width
    max_x = LIDAR_X+width
    max_y = LIDAR_Y+offset
    min_y = LIDAR_Y+offset-height

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
    for angle in range(0,len(data)):
        x = data[angle] * math.sin(math.radians(angle+ANGLE_OFFSET))
        y = data[angle] * math.cos(math.radians(angle+ANGLE_OFFSET))
        new_data[angle] = (data[angle], x, y)
        if data[angle] < 200:
            continue

        px = int(LIDAR_X + DIRECTION*(x / SCALE))
        py = int(LIDAR_Y - (y / SCALE))

        if min_tc_x <= px and px <= max_tc_x and min_tc_y <= py and py <= max_tc_y:
            pc = (128, 128, 128)
            plate_error_this = False
        elif min_x <= px and px <= max_x and min_y <= py and py <= max_y:
            pc = (255, 0, 0)
            #print("Plate Exception: slice=%d (%d,%d) (%d,%f)" % (slice,x,y,angle,data[angle]))
            plate_error = True
            draw.line((px-5,py-5,px+5,py+5), fill=(255,0,0))
            draw.line((px+5,py-5,px-5,py+5), fill=(255,0,0))
        elif (px <= min_x or px >= max_x) and py < max_y:
            pc = (0, 255, 0)
            draw.ellipse((px-5,py-5,px+5,py+5), outline=(0,255,0))
        else:
            pc = (0, 0, 0)
        point = (px, py)
        draw.point(point,fill=pc)
    
    # Trackcar
    plate_c=(128,128,128)
    draw.line((min_tc_x,max_tc_y,max_tc_x,max_tc_y), fill=plate_c)
    draw.line((min_tc_x,min_tc_y,max_tc_x,min_tc_y), fill=plate_c)
    draw.line((min_tc_x,max_tc_y,min_tc_x,min_tc_y), fill=plate_c)
    draw.line((max_tc_x,max_tc_y,max_tc_x,min_tc_y), fill=plate_c)
    draw.text((min_tc_x+5,min_tc_y+5), "TC", fill=plate_c)

    # Draw the Plate F Box
    if plate_error:
        plate_c = (255,0,0)
    else:
        plate_c = (0,255,0)
    draw.line((min_x,max_y,max_x,max_y), fill=plate_c)
    draw.line((min_x,min_y,max_x,min_y), fill=plate_c)
    draw.line((min_x,max_y,min_x,min_y), fill=plate_c)
    draw.line((max_x,max_y,max_x,min_y), fill=plate_c)
    draw.text((min_x+5,min_y+5), "PLATE F", fill=plate_c)

    # Calculate Gage
    gauge,slope,left_i,right_i = calc_gauge(new_data)

    TOTAL_SLOPE += slope
    TOTAL_SLOPE_COUNT += 1

    if gauge < 56.0 or gauge > 57.75:
        gauge_c = (255,0,0)
        #print("%s %s: Exception: Gage = %0.2f, slice=%d" % (latitude,longitude,gauge, slice))
        gauge_error = True
    else:
        gauge_c = (0,0,0)
    draw.text((5,5), "UTC: %s" % timestamp, fill=(0,0,0))
    draw.text((5,15), "LAT: %0.6f" % latitude, fill=(0,0,0))
    draw.text((5,25), "LONG: %0.6f" % longitude, fill=(0,0,0))
    draw.text((5,35), "MILEAGE: %0.2f" % mileage, fill=(0,0,0))
    if speed < 10:
        draw.text((5,45), "SPEED: %0.1f mph" % speed, fill=(0,0,0))
    else:
        draw.text((5,45), "SPEED: %d mph" % int(speed), fill=(0,0,0))
    if gauge == 0:
        draw.text((5,55), "GAGE: *ERROR*", fill=(255,0,0))
    else:
        draw.text((5,55), "GAGE: %0.2f in" % gauge, fill=gauge_c)

    if OUTPUT:
        image.save("slices/slice_%08d.png" % slice)
    
    return {'gauge_error': gauge_error, 'plate_error': plate_error, 'gauge': gauge}

def main(filename):
    G = gps_to_mileage.Gps2Miles("../known/negs.csv")
    G.sanity_check(update=True)
    last_lat = last_lon = 0
    slice = 0
    with open(sys.argv[1].split('.')[0]+".kml","w") as k:
        k.write('<xml version="1.0" encoding="UTF-8"?>\n')
        k.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        k.write('<Document>\n')
        with open(sys.argv[1], "r") as f:
            count = 0
            for line in f:
                fields = line.split(" ")
                if line[0] == '#':
                    continue
                if fields[1] == "A":
                    pass
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
                        speed = float(fields[8]) * 2.23694 # convert to mph
                    except ValueError:
                        pass
                    mileage, certainty = G.find_mileage(latitude, longitude)
                elif fields[1] == "L" and speed >= 0.1:
                    timestamp, datatype, data = line.split(" ", 2)
                    data = eval(data.replace('*', ''))
                    report = plot(data, timestamp, latitude, longitude, mileage, speed, slice)
                    slice += 1
                    if report['gauge_error'] or report['plate_error']:
                        count += 1
                        if OUTPUT:
                            if last_lat != latitude or last_lon != longitude:
                                print("%d %0.6f %0.6f %0.2f %0.2f %s" % (slice, latitude, longitude, mileage, report['gauge'], report['plate_error']))
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
        k.write('</Document>\n')
        k.write('</kml>\n')

print("Calculating Angle Offset...")
OUTPUT = False
main(sys.argv[1])
ANGLE_OFFSET = TOTAL_SLOPE/TOTAL_SLOPE_COUNT
print("Angle Offset = %0.2f" % ANGLE_OFFSET)

print("Generating Images...")
OUTPUT = True
TOTAL_SLOPE = TOTAL_SLOPE_COUNT = 0
main(sys.argv[1])
