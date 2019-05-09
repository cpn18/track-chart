#!/usr/bin/python
"""
GPS / ACCEL Logger V5
"""

import os
import sys
import threading
import time
import gps
import BaseHTTPServer

#import adxl345_shim as accel
import berryimu_shim as accel

HOST_NAME = ''
PORT_NUMBER = 80

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        global CURRENT
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        if s.path == "/poweroff":
            os.system("poweroff")
            s.wfile.write("<html><body>Bye</body></html")
            return

        s.wfile.write("<html><head><meta http-equiv=\"refresh\" content=\"1\"><title>RPi/GPS/IMU</title></head>")
        s.wfile.write("<body>")
        s.wfile.write("<table>")
        s.wfile.write("<tr><th>Latitude</th><td>%f</td></tr>" % CURRENT['lat'])
        s.wfile.write("<tr><th>Longitude</th><td>%f</td></tr>" % CURRENT['lon'])
        s.wfile.write("<tr><th>Altitude</th><td>%f</td></tr>" % CURRENT['alt'])
        s.wfile.write("</table>")
        s.wfile.write("<p>You accessed path: %s</p>" % s.path)
        s.wfile.write("</body></html>")

def web_server(httpd):
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    httpd.serve_forever()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)

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
            if hasattr(report, 'mode'):
                if report.mode == 1:
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

    # Output file
    output = open("/root/gps-data/%s_gps.csv" % timestamp, "w")

    alt = track = speed = 0.0
    while not DONE:
        try:
            # GPS
            report = session.next()
            # Wait for a 'TPV' report and display the current time
            # To see all report data, uncomment the line below
            #print report

            if report['class'] != 'TPV':
                #print(report)
                continue

            if hasattr(report, 'mode'):
                if report.mode == 1:
                    continue

            if hasattr(report, 'lat') and hasattr(report, 'lon') and hasattr(report, 'time'):
                CURRENT = report
                if not INLOCSYNC:
                    INLOCSYNC = True
                    lastreport = report
                    continue

                if lastreport.time == report.time:
                    continue

                if hasattr(report, 'speed'):
                    speed = report.speed

                if hasattr(report, 'track'):
                    # Bearing
                    track = report.track

                if hasattr(report, 'alt'):
                    alt = report.alt

                with open("/var/www/html/gps.html.new", "w") as web:
                    web.write("<html><head><meta http-equiv=\"refresh\" content=\"1\"></head><body>Lat: %02.6f<br>Long: %03.6f<br>Alt: %03f</body></html>" % (report.lat, report.lon, alt))
                os.rename("/var/www/html/gps.html.new", "/var/www/html/gps.html")

                output.write("%s G % 02.6f % 03.6f %03f %0.2f %0.2f *\n" % (report.time, report.lat, report.lon, alt, speed, track))
                lastreport = report

        except KeyError:
            pass
        except StopIteration:
            session = None
            print("GPSD has terminated")
            output.close()


def accel_logger(timestamp):
    """ Accel Data Logger """
    global INLOCSYNC

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
            x = axes['x']
            y = axes['y']
            z = axes['z']
            sum_x += x
            sum_y += y
            sum_z += z
            max_x = max(x, max_x)
            max_y = max(y, max_y)
            max_z = max(z, max_z)
            min_x = min(x, min_x)
            min_y = min(y, min_y)
            min_z = min(z, min_z)
            c += 1

            now = time.time()
            if now > next_time and c != 0:
                acceltime = time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                x1 = sum_x/c
                y1 = sum_y/c
                z1 = sum_z/c
                output.write("%s A %d % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f *\n" % (acceltime, c, min_x, x1, max_x, min_y, y1, max_y, min_z, z1, max_z))
                max_x = max_y = max_z = -20
                min_x = min_y = min_z = 20
                sum_x = sum_y = sum_z = 0
                c = 0
                next_time = now + 1
        except IOError:
            pass

# MAIN START
INLOCSYNC = False
DONE = False
VERSION = "#v5"

# Listen on port 2947 (gpsd) of localhost
SESSION = gps.gps("localhost", "2947")
SESSION.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

# Web Server
server_class = BaseHTTPServer.HTTPServer
httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)

# Make sure we have a time sync
TIMESTAMP = wait_for_timesync(SESSION)

print(TIMESTAMP)

try:
    T1 = threading.Thread(target=gps_logger, args=(TIMESTAMP, SESSION,))
    T1.start()
    T2 = threading.Thread(target=accel_logger, args=(TIMESTAMP,))
    T2.start()
    T3 = threading.Thread(target=web_server, args=(httpd,))
    T3.start()
except:
    print("Error: unable to start thread")
    sys.exit(-1)

while not DONE:
    try:
        time.sleep(60)
    except KeyboardInterrupt:
        DONE = True
        httpd.server_close()

T1.join()
T2.join()
T3.join()
