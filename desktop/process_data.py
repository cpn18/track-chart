#!/usr/bin/env python
#2018-09-21T14:44:22.000Z A 151 -2.471 -0.088  1.726 -0.863  1.081  3.138  3.138  9.596  15.024 *

import math
import sys



#filename="201706052258_log_wolfeboro.csv"
#filename="201809211444_log.csv"
#filename="20181006_negs_log.csv"
filename="20181013_mbrr_log.csv"
filename="201810191857_log_csrr.csv"
filename="201810240139_negs_log.csv"
filename="201810251117_log.csv"
try:
    filename = sys.argv[1]
except:
    print("Usage: %s filename" % sys.argv[0])
    sys.exit(1)

def ok(obj):
    xlimit = ylimit = zlimit = 60

    if obj['type'] == 'A':
        return (obj['minx'] >= -xlimit and
                obj['maxx'] <= xlimit and
                obj['miny'] >= -ylimit and
                obj['maxy'] <= ylimit and
                obj['minz'] >= -zlimit and
                obj['maxz'] <= zlimit)
    elif obj['type'] == 'G':
        return True
    return False

def calc_delta(a):
    return a['maxx'] - a['minx']

threshold=99.5

# Version 3 File

def parse_gps_v3(obj, a):
    v3speed_correction=(2.23694 / 1.15078)

    obj['lat'] = float(a[2])
    obj['lon'] = float(a[3])
    obj['alt'] = float(a[4])
    obj['speed'] = float(a[6]) * v3speed_correction
    obj['bearing'] = float(a[7])
    return obj

def parse_accel_v3(accel, obj, a):
    #obj['lat'] = accel[-1]['lat']
    #obj['lon'] = accel[-1]['lon']
    #obj['speed'] = accel[-1]['speed']
    obj['minx'] = float(a[3])
    obj['avgx'] = float(a[4])
    obj['maxx'] = float(a[5])
    obj['miny'] = float(a[6])
    obj['avgy'] = float(a[7])
    obj['maxy'] = float(a[8])
    obj['minz'] = float(a[9])
    obj['avgz'] = float(a[10])
    obj['maxz'] = float(a[11])
    return obj

# Version 4 File

def parse_gps_v4(obj, a):
    mps_to_mph = 2.23694
    m_to_ft = 3.28084

    obj = parse_gps_v3(obj, a)
    obj['alt'] = float(a[4]) * m_to_ft
    obj['speed'] = float(a[6]) * mps_to_mph
    return obj

def parse_accel_v4(accel, obj, a):
    return parse_accel_v3(accel, obj, a)

def read_data(filename):
    gps = {}
    accel = []
    count = 0
    with open(filename, 'r') as f:
        for line in f:
            a = line.split()
            if len(a) == 0:
                continue

            if a[0] == "#v3":
                version=3
            if a[0] == "#v4":
                version=4

            if a[0][0] == '<' or a[0][0] == '#' or a[-1] != '*':
                continue

            try:
                obj = {
                   'time': a[0],
                   'type': a[1],
                }
            except IndexError:
                continue

            if obj['type'] == 'A':
                if version == 3:
                    obj = parse_accel_v3(accel, obj, a)
                else:
                    obj = parse_accel_v4(accel, obj, a)
            elif obj['type'] == 'G':
                if version == 3:
                    obj = parse_gps_v3(obj, a)
                else:
                    obj = parse_gps_v4(obj, a)
                gps[obj['time']] = obj

            if ok(obj):
                accel.append(obj)

    # Sort list by time
    accel = sorted(accel, key=lambda k: k['time'])

    # Add geo-location data
    for i in range(0,len(accel)):
        if accel[i]['type'] == 'G':
            last_gps = accel[i]
        elif accel[i]['type'] == 'A':
            try:
                accel[i]['lat'] = gps[accel[i]['time']]['lat']
                accel[i]['lon'] = gps[accel[i]['time']]['lon'] 
                accel[i]['speed'] = gps[accel[i]['time']]['speed']
            except KeyError:
                accel[i]['lat'] = last_gps['lat']
                accel[i]['lon'] = last_gps['lon'] 
                accel[i]['speed'] = last_gps['speed']

    return accel

accel = read_data(filename)


def fill_buckets(accel):
    # Generate bucket counts
    buckets={}
    count=0
    for a in accel:
        if a['type'] == 'A':
            a['delta'] = calc_delta(a)
            #a['delta'] = a['avgx']
            count += 1
            b = int(abs(a['delta']))
            try:
                buckets[b] += 1
            except:
                buckets[b] = 1
    return (buckets,count)

def calc_noise_floor(buckets,count,threshold):

    # Find the noise floor
    total=0
    noise_floor=None
    for b in sorted(buckets.keys()):
        total += buckets[b]
        per = 100.0*float(total)/count
        if per > threshold and noise_floor is None:
            print("---> %0.2f%% <---" % threshold)
            noise_floor = b
        print("[%d] = %d %0.2f%%" % (b, buckets[b], per))
    return noise_floor

buckets, count = fill_buckets(accel)

noise_floor = calc_noise_floor(buckets,count,threshold)
if noise_floor is None:
    print("could not calculate noise floor")
    sys.exit(1)
else:
    print("noise floor = %d" % noise_floor)


from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

def line_chart(accel, threshold):
    y1=[]
    y2=[]
    y3=[]
    for a in accel:
        if a['type'] == 'A':
            if a['delta'] >= threshold and a['speed'] > 0:
                y1.append(a['delta'])
                print("%0.6f %0.6f %d" % (a['lat'], a['lon'], a['delta']))
            else:
                y1.append(0)
            y2.append(a['speed'])
            #if a['speed'] > 0:
            #    y1.append(a['minx'])
            #    y2.append(a['maxx'])
            #    y3.append(a['avgx'])
            #else:
            #    y1.append(0)
            #    y2.append(0)
            #    y3.append(0)

    df = pd.DataFrame({'x': range(0,len(y1)), 'avg': y1, 'speed': y2})
    plt.plot('x', 'avg', data=df, linestyle='-', marker='')
    plt.plot('x', 'speed', data=df, linestyle='-', marker='')
    #df = pd.DataFrame({'x': range(0,len(y1)), 'min': y1, 'max': y2, 'avg': y3})
    #plt.plot('x', 'min', data=df, linestyle='-', marker='')
    #plt.plot('x', 'max', data=df, linestyle='-', marker='')
    #plt.plot('x', 'avg', data=df, linestyle='-', marker='')
    plt.legend()
    plt.show()

def drawmap(accel, threshold):
    lat=[]
    lon=[]
    s=[]
    for a in accel:
        if a['type'] == 'A':
            lat.append(a['lat'])
            lon.append(a['lon'])
            if a['delta'] >= threshold and a['speed'] > 0:
                #s.append(10*a['delta']/a['speed'])
                s.append(a['delta'])
                print("%0.6f %0.6f %d" % (a['lat'], a['lon'], a['delta']))
            else:
                s.append(.1)
    m = Basemap(
            min(lon)-.01,
            min(lat)-.01,
            max(lon)+.01,
            max(lat)+.01
            )
    m.scatter(lon, lat, s, latlon=True)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Track')
    plt.show()

line_chart(accel, noise_floor)
#drawmap(accel, noise_floor)
