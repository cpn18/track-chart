#!/usr/bin/python3
"""
GPS / ACCEL LIDAR Logger V9
"""

import os
import sys
import threading
import time
import datetime
import gps
from http.server import BaseHTTPRequestHandler, HTTPServer

from rplidar import RPLidar

#import adxl345_shim as accel
import berryimu_shim as accel

HOST_NAME = ''
PORT_NUMBER = 80

class MyHandler(BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        global CURRENT
        global DONE
        global RESTART
        global MARK
        global MEMO

        if s.path == "/poweroff":
            outout = "{\"message\": \"Shutting down...\"}"
            DONE = True
            RESTART = False
            os.system("shutdown --poweroff +1")
        elif s.path == "/reset":
            output = "{\"message\": \"Resetting...\"}"
            DONE = True
        elif s.path.startswith("/mark?memo="):
            MARK = True
            MEMO = s.path.replace("/mark?memo=", "")
            output = "{\"message\": \"Marked...\"}"
        elif s.path == "/gps":
            output = ""
            if hasattr(CURRENT, 'lat'):
                output += ",\"lat\": %f" % CURRENT['lat']
            if hasattr(CURRENT, 'epy'):
                output += ",\"epy\": %f" % CURRENT['epy']
            if hasattr(CURRENT, 'lon'):
                output += ",\"lon\": %f" % CURRENT['lon']
            if hasattr(CURRENT, 'epx'):
                output += ",\"epx\": %f" % CURRENT['epx']
            if hasattr(CURRENT, 'alt'):
                output += ",\"alt\": %f" % CURRENT['alt']
            if hasattr(CURRENT, 'epv'):
                output += ",\"epv\": %f" % CURRENT['epv']
            if hasattr(CURRENT, 'speed'):
                output += ",\"speed\": %f" % CURRENT['speed']
            if hasattr(CURRENT, 'eps'):
                output += ",\"eps\": %f" % CURRENT['eps']
            if hasattr(CURRENT, 'time'):
                output += ",\"time\": \"%s\"" % CURRENT['time']
            output +=",\"temp\": %f" % TEMP
            output +=",\"gps_status\": %d" % GPS_STATUS
            output +=(",\"acc_status\": %s" % ACC_STATUS).lower()
            output +=(",\"lidar_status\": %s" % LIDAR_STATUS).lower()
            if len(output) > 0:
                output = output[1:]
            output = "{" + output + "}"
        elif s.path == "/jquery-3.4.1.min.js":
            with open("jquery-3.4.1.min.js", "r") as j:
                output = j.read()
        elif s.path == "/gps.html":
            with open("gps.html", "r") as j:
                output = j.read()
        elif s.path == "/favicon.ico":
            output = ""
        else:
            output = "<html><head><title>RPi/GPS/IMU</title></head>"
            output += "<body>"
            output += "<p>You accessed path: %s</p>" % s.path
            output += "</body></html>"

        s.send_response(200)
        s.send_header("Content-type", "text/html; charset=utf-8")
        s.send_header("Content-length", str(len(output)))
        s.end_headers()
        s.wfile.write(output.encode('utf-8'))

def web_server(httpd):
    global DONE
    while not DONE:
        try:
            print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
            httpd.serve_forever()
            print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))
        except KeyboardInterrupt:
            DONE = True
        except Exception as ex:
            print(ex)
        httpd.server_close()

def set_date(gps_date):
    """ Set the system clock """
    sys_date = "%s%s%s%s%s.%s" % (
        gps_date[5:7],
        gps_date[8:10],
        gps_date[11:13],
        gps_date[14:16],
        gps_date[0:4],
        gps_date[17:19])
    command = "date --utc %s > /dev/null" %  sys_date
    os.system(command)

def wait_for_timesync(session):
    """ Wait for Time Sync """
    global CURRENT
    while True:
        try:
            report = session.next()
            if report['class'] != 'TPV':
                continue
            if hasattr(report, 'mode') and report.mode == 1:
                # can't trust a mode=1 time
                continue
            if hasattr(report, 'time'):
                set_date(report.time)
                CURRENT = report
                return report.time.replace('-', '').replace(':', '').replace('T', '')[0:12]
        except Exception as ex:
            print(ex)
            sys.exit(1)


def gps_logger(timestamp, session):
    """ GPS Data Logger """
    global INLOCSYNC
    global CURRENT
    global DONE
    global MARK
    global GPS_STATUS

    # Output file
    output = open("/root/gps-data/%s_gps.csv" % timestamp, "w")
    output.write("%s\n" % VERSION)

    alt = track = speed = 0.0
    while not DONE:
        try:
            # GPS
            report = session.next()
            # Wait for a 'TPV' report and display the current time
            # To see all report data, uncomment the line below
            #print report

            if report['class'] != 'TPV':
                continue

            if hasattr(report, 'mode'):
                GPS_STATUS = report.mode
                if report.mode == 1:
                    print(report)
                    INLOCSYNC = False
                    print("Lost location sync")
                    continue

            if hasattr(report, 'lat') and hasattr(report, 'lon') and hasattr(report, 'time'):
                CURRENT = report
                if not INLOCSYNC:
                    INLOCSYNC = True
                    lastreport = report
                    print("Have location sync")
                    continue

                if lastreport.time == report.time:
                    continue

                if hasattr(report, 'speed'):
                    speed = "%f" % report.speed
                    eps = "%f" % report.eps
                else:
                    speed = "-"
                    eps = "-"

                if hasattr(report, 'track'):
                    # Bearing
                    track = "%0.2f" % report.track
                else:
                    track = "-"

                if hasattr(report, 'alt'):
                    alt = "%f" % report.alt
                    epv = "%f" % report.epv
                else:
                    alt = "-"
                    epv = "-"

                if hasattr(report, 'epx'):
                    epx = "%f" % report.epx
                else:
                    epx = "-"

                if hasattr(report, 'epy'):
                    epy = "%f" % report.epy
                else:
                    epy = "-"

                output.write("%s G %02.6f %03.6f %s %s %s %s %s %s %s *\n" % (report.time, report.lat, report.lon, alt, epy, epx, epv, speed, eps, track))
                lastreport = report

                if MARK:
                    MARK = False
                    with open("/root/gps-data/%s_marks.csv" % timestamp, "a") as mark:
                        mark.write("%s M %02.6f %03.6f \"%s\" *\n" % (report.time, report.lat, report.lon, MEMO))

        except KeyboardInterrupt:
            DONE = True
        except KeyError:
            pass
        except StopIteration:
            session = None
            print("GPSD has terminated")
            DONE = True 
    print("GPS done")
    output.close()


def accel_logger(timestamp):
    """ Accel Data Logger """
    global INLOCSYNC, DONE, ACC_STATUS

    max_x = max_y = max_z = -20
    min_x = min_y = min_z = 20
    sum_x = sum_y = sum_z = 0
    c = 0

    while not INLOCSYNC:
        time.sleep(5)

    output = open("/root/gps-data/%s_accel.csv" % timestamp, "w")
    output.write("%s\n" % VERSION)

    next_time = time.time() + 1
    while not DONE:
        try:
            axes = accel.get_axes()

            #put the axes into variables
            x = axes['ACCx']
            y = axes['ACCy']
            z = axes['ACCz']
            if INLOCSYNC:
                acceltime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                output.write("%s A %02.3f %02.3f %02.3f %02.3f %02.3f %02.3f *\n" % (acceltime, x, y, z, axes['GYRx'], axes['GYRy'], axes['GYRz']))
                ACC_STATUS = True
        except KeyboardInterrupt:
            DONE = True

        except IOError:
            pass
    print("ACCEL done")
    output.close()

def lidar_logger(timestamp):
    global INLOCSYNC, DONE, LIDAR_STATUS

    port_name = '/dev/ttyUSB0'

    while not INLOCSYNC:
        time.sleep(5)

    while not DONE:
        try:
            lidar = RPLidar(port_name)
            with open("/root/gps-data/%s_lidar.csv" % timestamp, "w") as f:
                f.write("%s\n" % VERSION)
                for i, scan in enumerate(lidar.iter_scans(max_buf_meas=1000)):
                    t = time.time()
                    lidartime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    f.write("%s L [" % (lidartime))
                    for (_, angle, distance) in scan:
                        f.write("(%0.4f,%0.2f)," % (angle, distance))
                    f.write("] *\n")
                    LIDAR_STATUS = True
                    if DONE:
                        break
                LIDAR_STATUS = False
            lidar.stop()
            lidar.stop_motor()
            lidar.disconnect()
        except KeyboardInterrupt:
            DONE = True
        except Exception as ex:
            print("WARNING: %s" % ex)
        time.sleep(5)
        timestamp = time.strftime("%Y%m%d%H%M", time.gmtime(time.time()))
    print("LIDAR Done")

# MAIN START
INLOCSYNC = False
DONE = False
RESTART = True
VERSION = "#v9"
CURRENT = {}
TEMP = 0
MARK = False
MEMO = ""

GPS_STATUS = 0
ACC_STATUS = False
LIDAR_STATUS = False

# Listen on port 2947 (gpsd) of localhost
SESSION = gps.gps("localhost", "2947")
SESSION.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

# Web Server
httpd = HTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)

T3 = threading.Thread(name="W", target=web_server, args=(httpd,))
T3.start()

# Make sure we have a time sync
TIMESTAMP = wait_for_timesync(SESSION)

print(TIMESTAMP)

try:
    T1 = threading.Thread(name="G", target=gps_logger, args=(TIMESTAMP, SESSION,))
    T1.start()
    T2 = threading.Thread(name="A", target=accel_logger, args=(TIMESTAMP,))
    T2.start()
    T3 = threading.Thread(name="L", target=lidar_logger, args=(TIMESTAMP,))
    T3.start()
except:
    print("Error: unable to start thread")
    sys.exit(-1)

while not DONE:
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as t:
            TEMP = int(t.read())/1000
            print("Temp = %0.1fC" % TEMP)
        time.sleep(60)
    except KeyboardInterrupt:
        DONE = True

httpd.server_close()

T1.join()
T2.join()
T3.join()

while not RESTART:
    time.sleep(60)
