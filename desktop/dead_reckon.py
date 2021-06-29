#!/usr/bin/env python
import sys
import datetime
import json
import math

from PIL import Image, ImageDraw, ImageOps

import geo

NORMALIZE = True

TIME_THRESHOLD = 5.0 # seconds

GPS_THRESHOLD = 10 # number of used satellites

#FILL=(255,255,255)
FILL=None
COLOR_GREEN=(0,255,0)
COLOR_BLUE=(0,0,255)
COLOR_RED=(255,0,0)
COLOR_BLACK=(0,0,0)
COLOR_WHITE=(255,255,255)

def parse_time(time_string):
    return datetime.datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")

try:
    filename = sys.argv[1]
except IndexError:
    print("USGAE: %s datafile.json" % sys.argv[0])
    sys.exit(1)

###
width = height = 4096
image = Image.new("RGB", (width, height), COLOR_WHITE)
draw = ImageDraw.Draw(image)

min_lat = 90
max_lat = -90
min_lon = 180
max_lon = -180

x_sum = 0
y_sum = 0
z_sum = 0
data=[]
bad_data=[]
acc_count = 0
used = count = 0
line_count = 0
with open(filename) as f:
    for line in f:
        try:
            obj = json.loads(line)
        except Exception as ex:
            print("LINE: %s" % line)
            print("ERROR: %s" % ex)
            sys.exit(1)

        #if not ( 8.5 < obj['mileage'] < 8.8):
        #    continue

        if obj['class'] == 'ATT':
            data.append(obj)
            x_sum += obj['acc_x']
            y_sum += obj['acc_y']
            z_sum += obj['gyro_z']
            acc_count += 1
        elif obj['class'] == 'TPV':
            if used >= GPS_THRESHOLD:
                line_count += 1
                obj['used'] = used
                obj['count'] = count
                data.append(obj)
                min_lat = min(min_lat, obj['lat'])
                max_lat = max(max_lat, obj['lat'])
                min_lon = min(min_lon, obj['lon'])
                max_lon = max(max_lon, obj['lon'])
            else:
                bad_data.append(obj)
        elif obj['class'] == 'SKY':
            data.append(obj)
            used = 0
            count = len(obj['satellites'])
            for s in obj['satellites']:
                if s['used']:
                    used += 1

margin = max((max_lat - min_lat), (max_lon - min_lon)) * 0.01
min_lat = min_lat-margin
max_lat = max_lat+margin
min_lon = min_lon-margin
max_lon = max_lon+margin
mid_lat = (min_lat+max_lat)/2
mid_lon = (min_lon+max_lon)/2
print(margin)
print(min_lat, min_lon)
print(mid_lat, mid_lon)
print(max_lat, max_lon)
print(geo.longitude_to_meters(max_lon - min_lon,mid_lat))
print(geo.latitude_to_meters(max_lat - min_lat))
scale = min(
    width/geo.longitude_to_meters(max_lon - min_lon,mid_lat),
    height/geo.latitude_to_meters(max_lat - min_lat)
)
print(scale)
#scale=0.5

# Normallize Data by reseting to zero average
if NORMALIZE:
    x_avg = x_sum / acc_count
    y_avg = y_sum / acc_count
    z_avg = z_sum / acc_count
    for obj in data:
        if obj['class'] != "ATT":
            continue
        obj['acc_x'] -= x_avg
        obj['acc_y'] -= y_avg
        obj['gyro_z'] -= z_avg


# Try to seed the initial values
for i in range(0, len(data)):
    if data[i]['class'] == "TPV":
        y_speed = data[i]['speed']
        z_bearing = data[i]['track']
        longitude = data[i]['lon']
        latitude = data[i]['lat']
        break

for i in range(0, len(data)):
    if data[i]['class'] == "ATT":
        last_time = parse_time(data[i]['time'])

        #longitude = data[i]['lon']
        x_last_acc = data[i]['acc_x']
        x_speed = 0

        #latitude = data[i]['lat']
        y_last_acc = data[i]['acc_y']

        z_last_acc = data[i]['gyro_z']
        break

y_speed = None
z_bearing = None

def geo_to_xy(lat, lon):
    latm = geo.latitude_to_meters(lat)
    lonm = geo.longitude_to_meters(lon, lat)
    x = (width/2) - (geo.longitude_to_meters(mid_lon,lat)-lonm)*scale
    y = (height/2) + (geo.latitude_to_meters(mid_lat)-latm)*scale
    return (x,y)

def draw_gps_fix(obj,color):
    """ Draw a GPS Fix """

    # Draw Center Point
    try:
        point = geo_to_xy(obj['lat'], obj['lon'])
        draw.point(point, fill=color)
    except KeyError:
        pass

    # Draw the Error Ellipse
    try:
        draw.ellipse([
            point[0]-obj['epx'],
            point[1]-obj['epy'],
            point[0]+obj['epx'],
            point[1]+obj['epy'],
            ], fill=FILL, outline=color)
    except KeyError:
        pass

    # Draw the left, center and right tracks
    try:
        newlat, newlon = geo.new_position(obj['lat'], obj['lon'], obj['speed']+obj['eps'], obj['track']-obj['epd'])
        draw.line([point, geo_to_xy( newlat, newlon)], fill=color)
        newlat, newlon = geo.new_position(obj['lat'], obj['lon'], obj['speed']+obj['eps'], obj['track'])
        draw.line([point, geo_to_xy( newlat, newlon)], fill=color)
        newlat, newlon = geo.new_position(obj['lat'], obj['lon'], obj['speed']+obj['eps'], obj['track']+obj['epd'])
        draw.line([point, geo_to_xy( newlat, newlon)], fill=color)
    except KeyError:
        pass

    # Draw the maximum one-second range
    try:
        north, _ = geo.new_position(obj['lat'], obj['lon'], obj['speed']+obj['eps'], 0)
        _, east = geo.new_position(obj['lat'], obj['lon'], obj['speed']+obj['eps'], 90)
        south, _ = geo.new_position(obj['lat'], obj['lon'], obj['speed']+obj['eps'], 180)
        _, west = geo.new_position(obj['lat'], obj['lon'], obj['speed']+obj['eps'], 270)
        draw.arc(
            [geo_to_xy(north, west), geo_to_xy(south, east)],
            start=obj['track']-obj['epd']-90,
            end=obj['track']+obj['epd']-90,
            fill=color)
    except KeyError:
        pass

    # Draw the minimum one-second range
    try:
        north, _ = geo.new_position(obj['lat'], obj['lon'], obj['speed']-obj['eps'], 0)
        _, east = geo.new_position(obj['lat'], obj['lon'], obj['speed']-obj['eps'], 90)
        south, _ = geo.new_position(obj['lat'], obj['lon'], obj['speed']-obj['eps'], 180)
        _, west = geo.new_position(obj['lat'], obj['lon'], obj['speed']-obj['eps'], 270)
        draw.arc(
            [geo_to_xy(north, west), geo_to_xy(south, east)],
            start=obj['track']-obj['epd']-90,
            end=obj['track']+obj['epd']-90,
            fill=color)
    except KeyError:
        pass

for obj in bad_data:
    if obj['class'] == "TPV":
        draw_gps_fix(obj, COLOR_RED)

output = open("dead_reckon.csv", "w")
output.write("Time DT Lat Long JerkY AccY SpeedY DR_Lat JerkX AccX SpeedX DR_Long JerkZ GyroZ BearingZ\n")

last_point = None
for obj in data:
    if obj['class'] == "SKY":
        used = 0
        count = len(obj['satellites'])
        for s in obj['satellites']:
            if s['used']:
                used += 1
        continue
    elif obj['class'] == "TPV":
        if obj['used'] >= GPS_THRESHOLD:
            latitude = obj['lat']
            longitude = obj['lon']
            y_speed = obj['speed']
            z_bearing = obj['track']

            draw_gps_fix(obj, COLOR_GREEN)
            point = geo_to_xy(latitude, longitude)
            if last_point is None:
                draw.point(point, fill=COLOR_BLACK)
            else:
                draw.line((last_point, point), fill=COLOR_BLACK)
            last_point = point
        continue
    elif y_speed is None or z_bearing is None:
        continue

    current = parse_time(obj['time'])

    DT = (current - last_time).total_seconds()

    if DT == 0:
        y_jerk = 0
        x_jerk = 0
        z_jerk = 0
    else:
        x_jerk = (obj['acc_x'] - x_last_acc) / DT
        y_jerk = (obj['acc_y'] - y_last_acc) / DT
        z_jerk = (obj['gyro_z'] - z_last_acc) / DT

    if DT < TIME_THRESHOLD:
        x_speed += obj['acc_x'] * DT
        y_speed += obj['acc_y'] * DT
        z_bearing += obj['gyro_z'] * DT
    
        while z_bearing > 360:
            z_bearing -= 360

        while z_bearing < 0:
            z_bearing += 360

        latitude, longitude = geo.new_position(
            latitude,
            longitude,
            y_speed * DT,
            z_bearing,
        )
        if not 'lat' in obj:
            obj['lat'] = latitude
            obj['lon'] = longitude

        output.write("%s %f %f %f %f %f %f %f %f %f %f %f %f %f %f\n" % (
            obj['time'], DT,
            obj['lat'], obj['lon'],
            y_jerk, obj['acc_y'], y_speed, latitude,
            x_jerk, obj['acc_x'], x_speed, longitude,
            z_jerk, obj['gyro_z'], z_bearing
        ))
        draw.point(geo_to_xy(latitude, longitude), fill=COLOR_BLUE)

    last_time = current
    x_last_acc = obj['acc_x']
    y_last_acc = obj['acc_y']
    z_last_acc = obj['gyro_y']

output.close()

image.save("dead_reckon.png")
