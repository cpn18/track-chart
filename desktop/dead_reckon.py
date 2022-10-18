#!/usr/bin/env python3
import sys
import datetime
import json
import math

import pirail

from PIL import Image, ImageDraw, ImageOps

import geo

TIME_THRESHOLD = 5.0 # seconds

#FILL=(255,255,255)
FILL=None
COLOR_GREEN=(0,255,0)
COLOR_BLUE=(0,0,255)
COLOR_RED=(255,0,0)
COLOR_BLACK=(0,0,0)
COLOR_WHITE=(255,255,255)

def geo_to_xy(lat, lon):
    """ Convert Latitude/Longitude to x,y in meters """
    latm = geo.latitude_to_meters(lat)
    lonm = geo.longitude_to_meters(lon, lat)
    x = (width/2) - (geo.longitude_to_meters(mid_lon,lat)-lonm)*scale
    y = (height/2) + (geo.latitude_to_meters(mid_lat)-latm)*scale
    return (x,y)

def draw_gps_fix(obj,color):
    """ Draw a GPS Fix """

    # Sanity check, ignore data without a fix
    if 'lat' not in obj or 'lon' not in obj:
        return

    # Draw Center Point
    point = geo_to_xy(obj['lat'], obj['lon'])
    draw.point(point, fill=color)

    # Draw the Error Ellipse
    if 'epx' in obj and 'epy' in obj: 
        draw.ellipse([
            point[0]-obj['epx'],
            point[1]-obj['epy'],
            point[0]+obj['epx'],
            point[1]+obj['epy'],
            ], fill=FILL, outline=color)

    if 'speed' in obj and 'track' in obj and 'eps' in obj and 'epd' in obj:
        # Draw the left, center and right tracks
        newlat, newlon = geo.new_position(obj['lat'], obj['lon'], obj['speed']+obj['eps'], obj['track']-obj['epd'])
        draw.line([point, geo_to_xy( newlat, newlon)], fill=color)
        newlat, newlon = geo.new_position(obj['lat'], obj['lon'], obj['speed']+obj['eps'], obj['track'])
        draw.line([point, geo_to_xy( newlat, newlon)], fill=color)
        newlat, newlon = geo.new_position(obj['lat'], obj['lon'], obj['speed']+obj['eps'], obj['track']+obj['epd'])
        draw.line([point, geo_to_xy( newlat, newlon)], fill=color)

        # Draw the maximum one-second range
        north, _ = geo.new_position(obj['lat'], obj['lon'], obj['speed']+obj['eps'], 0)
        _, east = geo.new_position(obj['lat'], obj['lon'], obj['speed']+obj['eps'], 90)
        south, _ = geo.new_position(obj['lat'], obj['lon'], obj['speed']+obj['eps'], 180)
        _, west = geo.new_position(obj['lat'], obj['lon'], obj['speed']+obj['eps'], 270)
        draw.arc(
            [geo_to_xy(north, west), geo_to_xy(south, east)],
            start=obj['track']-obj['epd']-90,
            end=obj['track']+obj['epd']-90,
            fill=color)

        # Draw the minimum one-second range
        north, _ = geo.new_position(obj['lat'], obj['lon'], obj['speed']-obj['eps'], 0)
        _, east = geo.new_position(obj['lat'], obj['lon'], obj['speed']-obj['eps'], 90)
        south, _ = geo.new_position(obj['lat'], obj['lon'], obj['speed']-obj['eps'], 180)
        _, west = geo.new_position(obj['lat'], obj['lon'], obj['speed']-obj['eps'], 270)
        draw.arc(
            [geo_to_xy(north, west), geo_to_xy(south, east)],
            start=obj['track']-obj['epd']-90,
            end=obj['track']+obj['epd']-90,
            fill=color)

try:
    filename = sys.argv[-1]
except IndexError:
    print("USGAE: %s [args] data_file.json" % sys.argv[0])
    sys.exit(1)

###
width = height = 4096
image = Image.new("RGB", (width, height), COLOR_WHITE)
draw = ImageDraw.Draw(image)

min_lat = 90
max_lat = -90
min_lon = 180
max_lon = -180

# Average Errors
aax = -0.76994928407068
aay = -0.12089123215864023
agz = -0.5585602094240765

data=[]
bad_data=[]
acc_count = 0

for line_no, obj in pirail.read(filename, classes=['ATT', 'TPV']):
    if obj['class'] == 'ATT':
        # Error compensation
        obj['acc_x'] -= aax
        obj['acc_y'] -= aay
        obj['gyro_z'] -= agz
        data.append(obj)
        acc_count += 1
    elif obj['class'] == 'TPV':
        min_lat = min(min_lat, obj['lat'])
        max_lat = max(max_lat, obj['lat'])
        min_lon = min(min_lon, obj['lon'])
        max_lon = max(max_lon, obj['lon'])
        data.append(obj)

margin = max((max_lat - min_lat), (max_lon - min_lon)) * 0.01
min_lat = min_lat-margin
max_lat = max_lat+margin
min_lon = min_lon-margin
max_lon = max_lon+margin
mid_lat = (min_lat+max_lat)/2
mid_lon = (min_lon+max_lon)/2
print("Latitude (degrees): %f %f %f" % (min_lat, mid_lat, max_lat))
print("Longitude (degrees): %f %f %f" % (min_lon, mid_lon, max_lon))
lon_meters = geo.longitude_to_meters(max_lon - min_lon,mid_lat)
lat_meters = geo.latitude_to_meters(max_lat - min_lat)
print("Latitude (meters): %f" % lat_meters)
print("Longitude (meters): %f" % lon_meters)
scale = min(
    width/geo.longitude_to_meters(max_lon - min_lon,mid_lat),
    height/geo.latitude_to_meters(max_lat - min_lat)
)
print("Scale: %f" % scale)

# Try to seed the initial values

# Find the first TPV record
for i in range(0, len(data)):
    if data[i]['class'] == "TPV":
        y_speed = data[i]['speed']
        z_bearing = data[i]['track']
        longitude = data[i]['lon']
        latitude = data[i]['lat']
        break

# Find the first ATT record
for i in range(0, len(data)):
    if data[i]['class'] == "ATT":
        last_time = pirail.parse_time(data[i]['time'])

        x_last_acc = data[i]['acc_x']
        x_speed = 0

        y_last_acc = data[i]['acc_y']

        z_last_acc = data[i]['gyro_z']
        break

y_speed = None
z_bearing = None

for obj in bad_data:
    if obj['class'] == "TPV":
        draw_gps_fix(obj, COLOR_RED)

output = open("dead_reckon.csv", "w")
output.write("Time DT Lat Long JerkY AccY SpeedY DR_Lat JerkX AccX SpeedX DR_Long JerkZ GyroZ BearingZ\n")

last_point = None
for obj in data:
    if obj['class'] == "TPV":
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

    current = pirail.parse_time(obj['time'])

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

image_file = "dead_reckon.png"
print("Saved Image: %s" % image_file)
image.save(image_file)
