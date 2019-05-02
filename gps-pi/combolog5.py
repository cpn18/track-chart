#!/usr/bin/python

import os
import sys
import threading
import time
import gps

#import adxl345_shim as accel
import berryimu_shim as accel

def set_date(d):
    """ Set the system clock """
    d = "%s%s%s%s%s.%s" % (d[5:7], d[8:10], d[11:13], d[14:16], d[0:4], d[17:19])
    command = "date --utc %s > /dev/null" %  d
    os.system(command)

def gps_logger():
    """ GPS Data Logger """
    global INLOCSYNC, INTIMESYNC, TIMESTAMP

    # miles
    threshold = 0.0

    # Listen on port 2947 (gpsd) of localhost
    session = gps.gps("localhost", "2947")
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

    alt = track = speed = 0.0
    while not DONE:
        try:
            # GPS
            report = session.next()
            # Wait for a 'TPV' report and display the current time
            # To see all report data, uncomment the line below
            #print report

            if report['class'] != 'TPV':
                print(report)
                continue

            if hasattr(report, 'mode'):
                if report.mode == 1:
                    continue

            if hasattr(report, 'lat') and hasattr(report, 'lon') and hasattr(report, 'time'):
                if not INTIMESYNC:
                    set_date(report.time)
                    TIMESTAMP = report.time.replace('-', '').replace(':', '').replace('T', '')[0:12]
                    output = open("/root/gps-data/%s_gps.csv" % TIMESTAMP, "w")
                    output.write("%s\n" % VERSION)
                    output.write("%s T *\n" % report.time)
                    INTIMESYNC = True

                if not INLOCSYNC:
                    INLOCSYNC = True
                    lastreport = report
                    continue

                if hasattr(lastreport, 'time') and lastreport.time == report.time:
                    continue

                if hasattr(report, 'speed'):
                    speed = report.speed

                if hasattr(report, 'track'):
                    # Bearing
                    track = report.track

                if hasattr(report, 'alt'):
                    alt = report.alt

                output.write("%s G % 02.6f % 03.6f %03f %0.2f %0.2f *\n" % (report.time, report.lat, report.lon, alt, speed, track))
                lastreport = report

        except KeyError:
            pass
        except StopIteration:
            session = None
            print("GPSD has terminated")
            output.close()


def accel_logger():
    """ Accel Data Logger """
    global INLOCSYNC

    max_x = max_y = max_z = -20
    min_x = min_y = min_z = 20
    sum_x = sum_y = sum_z = 0
    c = 0

    while not INLOCSYNC:
        time.sleep(5)

    output = open("/root/gps-data/%s_accel.csv" % TIMESTAMP, "w")
    output.write("%s\n" % VERSION)

    next = time.time() + 1
    while not DONE:
        try:
            axes = accel.get_axes()

            #put the axes into variables
            x = axes['x']
            y = axes['y']
            z = axes['z']
            sum_x += x
            sum_y += y
            sum_z += z
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y
            if z > max_z:
                max_z = z
            if x < min_x:
                min_x = x
            if y < min_y:
                min_y = y
            if z < min_z:
                min_z = z
            c += 1

            now = time.time()
            if now > next and c != 0:
                acceltime = time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                x1 = sum_x/c
                y1 = sum_y/c
                z1 = sum_z/c
                output.write("%s A %d % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f *\n" % (acceltime, c, min_x, x1, max_x, min_y, y1, max_y, min_z, z1, max_z))
                max_x = max_y = max_z = -20
                min_x = min_y = min_z = 20
                sum_x = sum_y = sum_z = 0
                c = 0
                next = now + 1
        except IOError:
            pass

# MAIN START
TIMESTAMP = None
INLOCSYNC = False
INTIMESYNC = False
DONE = False
VERSION = "#v5"
try:
    T1 = threading.Thread(target=gps_logger, args=())
    T1.start()
    T2 = threading.Thread(target=accel_logger, args=())
    T2.start()
except:
    print("Error: unable to start thread")
    sys.exit(-1)

while not DONE:
    try:
        time.sleep(60)
    except KeyboardInterrupt:
        DONE = True

T1.join()
T2.join()
