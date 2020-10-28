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
import json
import nmea
import statistics
from http.server import BaseHTTPRequestHandler, HTTPServer

from rplidar import RPLidar

#import adxl345_shim as accel
import berryimu_shim as accel

HOST_NAME = ''
PORT_NUMBER = 80

ALWAYS_LOG = True

try:
    with open("axis_config.json", "r") as f:
        AXIS_CONFIG = json.loads(f.read())
except:
    AXIS_CONFIG = {"x": "x", "y": "y", "z": "z"}

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
        global HOLD
        global MEMO

        if s.path == "/poweroff":
            output = "{\"message\": \"Shutting down...\"}"
            DONE = True
            RESTART = False
            os.system("shutdown --poweroff +1")
        elif s.path == "/reset":
            output = "{\"message\": \"Resetting...\"}"
            DONE = True
        elif s.path.startswith("/mark?memo="):
            HOLD = 1
            MEMO = s.path.replace("/mark?memo=", "")
            output = "{\"message\": \"Marked...\"}"
        elif s.path.startswith("/hold?memo="):
            HOLD = 15 
            MEMO = s.path.replace("/hold?memo=", "")
            output = "{\"message\": \"Holding...\"}"
        elif s.path.startswith("/setup?"):
            for var in s.path.split("?")[1].split("&"):
                key, value = var.split("=")
                AXIS_CONFIG[key]=value.lower()
            output = "{\"message\": \"Stored...\"}"
            with open("axis_config.json", "w") as f:
                f.write(json.dumps(AXIS_CONFIG))
            DONE = True
        elif s.path == "/gps":
            output ="\"temp\": %f" % TEMP
            output +=",\"gps_status\": %d" % GPS_STATUS
            output +=",\"gps_num_sat\": %d" % GPS_NUM_SAT
            output +=",\"gps_num_used\": %d" % GPS_NUM_USED
            output +=(",\"acc_status\": %s" % ACC_STATUS).lower()
            output +=(",\"lidar_status\": %s" % LIDAR_STATUS).lower()
            output +=(",\"hold\": %s" % HOLD).lower()
            # Floating Point Fields
            for key in [
                    'lat', 'epy',
                    'lon', 'epx',
                    'alt', 'epv',
                    'speed', 'eps',
                    'ept',
                    ]:
                if key in CURRENT:
                    output += ",\""+key+"\": " + str(CURRENT[key])

            # Strings Fields
            for key in ['time']:
                if key in CURRENT:
                    output += ",\""+key+"\": \"%s\"" % CURRENT[key]

            output = "{" + output + "}"
        elif s.path == "/jquery-3.4.1.min.js":
            with open("jquery-3.4.1.min.js", "r") as j:
                output = j.read()
        elif s.path == "/gps.html":
            with open("gps.html", "r") as j:
                output = j.read()
        elif s.path == "/setup.html":
            with open("setup.html", "r") as j:
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
                CURRENT = nmea.tpv_to_json(report)
                return report.time.replace('-', '').replace(':', '').replace('T', '')[0:12]
        except Exception as ex:
            print(ex)
            sys.exit(1)

def gps_logger(timestamp, session):
    """ GPS Data Logger """
    global INLOCSYNC
    global CURRENT
    global DONE
    global HOLD
    global GPS_STATUS, GPS_NUM_SAT, GPS_NUM_USED

    hold_lat = []
    hold_lon = []

    # Output file
    output = open("/root/gps-data/%s_gps.csv" % timestamp, "w")
    output.write("%s\n" % VERSION)

    while not DONE:
        try:
            # GPS
            report = session.next()
            # Wait for a 'TPV' report and display the current time
            # To see all report data, uncomment the line below
            #print(report)

            if report['class'] == 'TPV':
                obj = nmea.tpv_to_json(report)
            elif report['class'] == 'SKY':
                obj = nmea.sky_to_json(report)
                (GPS_NUM_USED, GPS_NUM_SAT) = nmea.calc_used(obj)
                obj['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            else:
                continue

            if 'time' in obj:
                output.write("%s %s %s *\n" % (obj['time'], obj['class'], json.dumps(obj)))

            if obj['class'] == 'TPV':
                if 'mode' in obj:
                    GPS_STATUS = obj['mode']
                    if obj['mode'] == 1:
                        INLOCSYNC = False
                        print("%s Lost location sync" % obj['time'])
                        continue

                if 'lat' in obj and 'lon' in obj and 'time' in obj:
                    CURRENT = obj
                    if not INLOCSYNC:
                        INLOCSYNC = True
                        lastreport = obj
                        print("%s Have location sync" % obj['time'])

                    if HOLD == 0:
                        with open("/root/gps-data/%s_marks.csv" % timestamp, "a") as mark:
                            mark.write("%s M %02.6f %03.6f \"%s\" *\n" % (obj['time'], statistics.mean(hold_lat), statistics.mean(hold_lon), MEMO))
                        hold_lat = []
                        hold_lon = []
                        HOLD = -1
                    elif HOLD > 0:
                        hold_lat.append(report.lat)
                        hold_lon.append(report.lon)
                        HOLD -= 1

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


def imu_logger(timestamp):
    """ Accel Data Logger """
    global DONE, ACC_STATUS

    device = accel.device()

    max_x = max_y = max_z = -20
    min_x = min_y = min_z = 20
    sum_x = sum_y = sum_z = 0
    c = 0

    while not INLOCSYNC:
        time.sleep(5)

    output = open("/root/gps-data/%s_accel.csv" % timestamp, "w")
    output.write("%s\n" % VERSION)
    acceltime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    output.write("%s ATTCFG %s *\n" % (acceltime, json.dumps(AXIS_CONFIG)))

    while not DONE:
        #now = time.time()
        try:
            axes = accel.get_axes()
            acceltime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            att_obj = {
                "class": "ATT",
                "device": device,
                "time": acceltime,
                "acc_x": axes['ACC'+AXIS_CONFIG['x']],
                "acc_y": axes['ACC'+AXIS_CONFIG['y']],
                "acc_z": axes['ACC'+AXIS_CONFIG['z']],
                "gyro_x": axes['GYR'+AXIS_CONFIG['x']],
                "gyro_y": axes['GYR'+AXIS_CONFIG['y']],
                "gyro_z": axes['GYR'+AXIS_CONFIG['z']],
            }

            #put the axes into variables
            if INLOCSYNC or ALWAYS_LOG:
                output.write("%s ATT %s *\n" % (acceltime, json.dumps(att_obj)))
                ACC_STATUS = True
        except KeyboardInterrupt:
            DONE = True
        except IOError:
            pass

        #while (time.time() - now < 0.02):
        #    time.sleep(0.001)

    ACC_STATUS = False
    print("ACCEL done")
    output.close()

def lidar_logger(timestamp):
    global DONE, LIDAR_STATUS

    port_name = '/dev/lidar'
    lidar = None

    while not INLOCSYNC:
        time.sleep(5)

    while not DONE:
        try:
            lidar = RPLidar(port_name)
            with open("/root/gps-data/%s_lidar.csv" % timestamp, "w") as f:
                f.write("%s\n" % VERSION)
                for i, scan in enumerate(lidar.iter_scans(max_buf_meas=1500)):
                    if INLOCSYNC or ALWAYS_LOG:
                        lidartime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                        f.write("%s L [" % (lidartime))
                        for (_, angle, distance) in scan:
                            f.write("(%0.4f,%0.2f)," % (angle, distance))
                        f.write("] *\n")
                    LIDAR_STATUS = True
                    if DONE:
                        break
        except KeyboardInterrupt:
            DONE = True
        except Exception as ex:
            lidartime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            print("%s WARNING: %s" % (lidartime, ex))
        if lidar is not None:
            lidar.stop()
            lidar.stop_motor()
            lidar.disconnect()
        LIDAR_STATUS = False
        time.sleep(1)
        timestamp = time.strftime("%Y%m%d%H%M", time.gmtime(time.time()))
    print("LIDAR Done")

# MAIN START
INLOCSYNC = False
DONE = False
RESTART = True
VERSION = "#v9"
CURRENT = {}
TEMP = 0
HOLD = -1
MEMO = ""

GPS_STATUS = 0
GPS_NUM_SAT = 0
GPS_NUM_USED = 0
ACC_STATUS = False
LIDAR_STATUS = False

# Listen on port 2947 (gpsd) of localhost
SESSION = gps.gps("localhost", "2947")
SESSION.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

# Web Server
httpd = HTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)

Twww = threading.Thread(name="W", target=web_server, args=(httpd,))
Twww.start()

# Make sure we have a time sync
TIMESTAMP = wait_for_timesync(SESSION)

print(TIMESTAMP)

try:
    Tgps = threading.Thread(name="G", target=gps_logger, args=(TIMESTAMP, SESSION,))
    Tgps.start()
    Timu = threading.Thread(name="A", target=imu_logger, args=(TIMESTAMP,))
    Timu.start()
    #Tlidar = threading.Thread(name="L", target=lidar_logger, args=(TIMESTAMP,))
    #Tlidar.start()
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

httpd.shutdown()
httpd.server_close()

Twww.join()
Tgps.join()
Timu.join()
#Tlidar.join()

while not RESTART:
    time.sleep(60)
