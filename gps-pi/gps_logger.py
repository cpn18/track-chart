#!/usr/bin/python3
"""
GPS Logger V9
"""

import os
import sys
import threading
import time
import datetime
import gps
import json
import nmea
from http.server import BaseHTTPRequestHandler, HTTPServer


ALWAYS_LOG = True

ERROR_DELAY = 10
SYNC_DELAY = 5
IDLE_DELAY = 60

# Configure Axis
try:
    with open("config.json", "r") as f:
        CONFIG = json.loads(f.read())
except:
    CONFIG = {
        "gps": {"log": True},
    }

CONFIG['class'] = "CONFIG"
CONFIG['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

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

        content_type = "text/html; charset=utf-8"

        if s.path == "/poweroff":
            content_type = "application/json"
            output = "{\"message\": \"Shutting down...\"}"
            DONE = True
            RESTART = False
            os.system("shutdown --poweroff +1")
        elif s.path == "/reset":
            content_type = "application/json"
            output = "{\"message\": \"Resetting...\"}"
            DONE = True
        elif s.path.startswith("/mark?memo="):
            HOLD = 1
            MEMO = s.path.replace("/mark?memo=", "")
            content_type = "application/json"
            output = "{\"message\": \"Marked...\"}"
        elif s.path.startswith("/hold?memo="):
            HOLD = 15 
            MEMO = s.path.replace("/hold?memo=", "")
            content_type = "application/json"
            output = "{\"message\": \"Holding...\"}"
        elif s.path.startswith("/setup?"):
            for var in s.path.split("?")[1].split("&"):
                key, value = var.split("=")
                CONFIG['imu'][key]=value.lower()
            content_type = "application/json"
            output = "{\"message\": \"Stored...\"}"
            with open("config.json", "w") as f:
                CONFIG['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                f.write(json.dumps(CONFIG))
            DONE = True
        elif s.path == "/lidar":
            content_type = "application/json"
            output = json.dumps(LIDAR_DATA)
        elif s.path == "/tpv":
            content_type = "application/json"
            output = json.dumps(TPV) + "\n"
        elif s.path == "/sky":
            content_type = "application/json"
            output = json.dumps(SKY) + "\n"
        elif s.path == "/gps":
            content_type = "application/json"
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
                    output += ",\"gps"+key+"\": \"%s\"" % CURRENT[key]

            output += ",\"time\": \"" + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ") + "\""

            output = "{" + output + "}"
        elif s.path == "/jquery-3.4.1.min.js":
            with open("jquery-3.4.1.min.js", "r") as j:
                output = j.read()
        elif s.path == "/lidar.html":
            with open("lidar.html", "r") as j:
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
        s.send_header("Content-type", content_type)
        s.send_header("Content-length", str(len(output)))
        s.end_headers()
        s.wfile.write(output.encode('utf-8'))

def web_server(httpd):
    while not DONE:
        try:
            print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
            httpd.serve_forever()
            print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))
        except Exception as ex:
            print(ex)
        httpd.server_close()

def mylog(msg):
    logtime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    if isinstance(msg, str):
        msg = {"log": msg}
    print("%s LOG '%s' *" % (logtime, json.dumps(msg)))

def gps_logger(output_directory, session):
    """ GPS Data Logger """
    global INLOCSYNC
    global CURRENT, SKY, TPV
    global DONE
    global HOLD
    global GPS_STATUS, GPS_NUM_SAT, GPS_NUM_USED

    hold_lat = []
    hold_lon = []
    hold_alt = []

    # Configure
    try:
        with open("config.json", "r") as f:
            config = json.loads(f.read())
    except:
        config = {"class": "CONFIG", "gps": {"log": True}}
    config['time'] =  datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Create the output directory
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    # Open the output file
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    with open(os.path.join(output_directory,timestamp+"_gps.csv"), "w") as gps_output:
        gps_output.write("#v%d\n" % VERSION)
        gps_output.write("%s %s %s *\n" % (config['time'], config['class'], json.dumps(config)))

        while not DONE:
            # GPS
            report = session.next()
            # To see all report data, uncomment the line below
            #print(report)

            if report['class'] == 'TPV':
                obj = nmea.tpv_to_json(report)
                # Add Sat Metrics
                obj['num_sat'] = GPS_NUM_SAT
                obj['num_used'] = GPS_NUM_USED
                TPV = obj
            elif report['class'] == 'SKY':
                obj = nmea.sky_to_json(report)
                # Add Time
                obj['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                (GPS_NUM_USED, GPS_NUM_SAT) = nmea.calc_used(obj)
                SKY = obj
            else:
                continue

            # Log the Data
            if 'time' in obj:
                gps_output.write("%s %s %s *\n" % (obj['time'], obj['class'], json.dumps(obj)))

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
                        with open(os.path.join(output_directory,timestamp+"_marks.csv"), "a") as mark:
                            mark_obj = {
                                "class": "MARK",
                                "lat": statistics.mean(hold_lat),
                                "lon": statistics.mean(hold_lon),
                                "num_sat": GPS_NUM_SAT,
                                "num_used": GPS_NUM_USED,
                                "time": obj['time'],
                                "memo": MEMO,
                            }
                            if len(hold_alt) > 0:
                                mark_obj['alt'] = statistics.mean(hold_alt)
                            mark.write("%s %s %s *\n" % (mark_obj['time'], mark_obj['class'], json.dumps(mark_obj)))
                        hold_lat = []
                        hold_lon = []
                        hold_alt = []
                        HOLD = -1
                    elif HOLD > 0:
                        hold_lat.append(report.lat)
                        hold_lon.append(report.lon)
                        if 'alt' in report:
                            hold_alt.append(report.alt)
                        HOLD -= 1

def gps_logger_wrapper(output_directory, session):
    """ Wrapper Around GPS Logger Function """
    global GPS_STATUS

    GPS_STATUS = 0
    try:
        gps_logger(output_directory, session)
    except StopIteration:
        session = None
        mylog("GPSD has terminated")
        DONE = True
    except Exception as ex:
        mylog("GPS Logger Exception: %s" % ex)
    GPS_STATUS = 0
    mylog("GPS done")

# MAIN START
INLOCSYNC = False
DONE = False
RESTART = True
VERSION = 9
CURRENT = {}
TEMP = 0
HOLD = -1
MEMO = ""

GPS_STATUS = 0
GPS_NUM_SAT = 0
GPS_NUM_USED = 0
ACC_STATUS = False
LIDAR_STATUS = False
LIDAR_DATA = {}
AUDIO_STATUS = False

# Command Line Configuration
try:
    HOST_NAME = ''
    PORT_NUMBER = int(sys.argv[1])
    OUTPUT = sys.argv[2]
except IndexError:
    PORT_NUMBER = 8080
    OUTPUT = "/root/gps-data"

# Listen on port 2947 (gpsd) of localhost
SESSION = gps.gps("localhost", "2947")
SESSION.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

# Web Server
httpd = HTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)

Twww = threading.Thread(name="W", target=web_server, args=(httpd,))
Twww.start()

try:
    gps_logger_wrapper(OUTPUT, SESSION)
except KeyboardInterrupt:
    DONE = True
    pass

httpd.shutdown()
httpd.server_close()
Twww.join()
