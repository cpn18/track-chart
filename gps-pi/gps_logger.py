#!/usr/bin/python3
"""
GPS Logger V9
"""

import os
import sys
import threading
import time
import datetime
import json
import statistics
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

import gps
import nmea

ALWAYS_LOG = True

STREAM_DELAY = 1

def read_config():
    """ Read Configuration """
    try:
        with open("config.json", "r") as config_file:
            config = json.loads(config_file.read())
    except:
        config = {
            "gps": {"log": True},
        }
    config['class'] = "CONFIG"
    config['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return config

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    """ Web Request Handler """
    def do_GET(self):
        """Respond to a GET request."""
        global DONE
        global HOLD
        global MEMO

        content_type = "text/html; charset=utf-8"

        if self.path.startswith("/mark?memo="):
            HOLD = 1
            MEMO = self.path.replace("/mark?memo=", "")
            content_type = "application/json"
            output = "{\"message\": \"Marked...\"}"
        elif self.path.startswith("/hold?memo="):
            HOLD = 15
            MEMO = self.path.replace("/hold?memo=", "")
            content_type = "application/json"
            output = "{\"message\": \"Holding...\"}"
        elif self.path == "/tpv":
            content_type = "application/json"
            output = json.dumps(TPV) + "\n"
        elif self.path == "/sky":
            content_type = "application/json"
            output = json.dumps(SKY) + "\n"
        elif self.path == "/gps-stream":
            content_type = "text/event-stream"
            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.end_headers()
            while not DONE:
                if TPV['time'] < SKY['time']:
                    lines = [
                        "event: tpv\n",
                        "data: "+json.dumps(TPV) + "\n",
                        "\n",
                        "event: sky\n",
                        "data: "+json.dumps(SKY) + "\n",
                        "\n",
                    ]
                else:
                    lines = [
                        "event: sky\n",
                        "data: "+json.dumps(SKY) + "\n",
                        "\n",
                        "event: tpv\n",
                        "data: "+json.dumps(TPV) + "\n",
                        "\n",
                    ]
                for line in lines:
                    self.wfile.write(line.encode('utf-8'))
                time.sleep(STREAM_DELAY)
            return
        elif self.path == "/gps":
            content_type = "application/json"
            if TPV['time'] < SKY['time']:
                output = json.dumps([TPV, SKY]) + "\n"
            else:
                output = json.dumps([SKY, TPV]) + "\n"
        elif self.path == "/gps.html":
            with open("gps.html", "r") as j:
                output = j.read()
        else:
            self.send_error(404, self.path)
            return

        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.send_header("Content-length", str(len(output)))
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))

def web_server(host_name, port_number):
    """ Web Server Wrapper """
    global DONE
    httpd = ThreadedHTTPServer((host_name, port_number), MyHandler)
    while not DONE:
        try:
            print(time.asctime(), "Server Starts - %s:%s" % (host_name, port_number))
            httpd.serve_forever()
            print(time.asctime(), "Server Stops - %s:%s" % (host_name, port_number))
        except KeyboardInterrupt:
            DONE = True
        except Exception as ex:
            print("WARNING: %s" % ex)
    httpd.shutdown()
    httpd.server_close()

def gps_logger(output_directory):
    """ GPS Data Logger """
    global INLOCSYNC
    global SKY, TPV
    global DONE
    global HOLD
    global GPS_STATUS, GPS_NUM_SAT, GPS_NUM_USED

    hold_lat = []
    hold_lon = []
    hold_alt = []

    config = read_config()

    # Create the output directory
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    # Listen on port 2947 (gpsd) of localhost
    session = gps.gps("localhost", "2947")
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

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
                obj['hold'] = HOLD
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
                    if not INLOCSYNC:
                        INLOCSYNC = True
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

def gps_logger_wrapper(output_directory):
    """ Wrapper Around GPS Logger Function """
    global GPS_STATUS
    global DONE

    GPS_STATUS = 0
    try:
        gps_logger(output_directory)
    except StopIteration:
        print("GPSD has terminated")
        DONE = True
    except Exception as ex:
        print("GPS Logger Exception: %s" % ex)
    GPS_STATUS = 0
    print("GPS done")

# MAIN START
INLOCSYNC = False
DONE = False
VERSION = 9
TPV = SKY = {}
HOLD = -1
MEMO = ""

GPS_STATUS = 0
GPS_NUM_SAT = 0
GPS_NUM_USED = 0

# Command Line Configuration
try:
    HOST_NAME = ''
    PORT_NUMBER = int(sys.argv[1])
    OUTPUT = sys.argv[2]
except IndexError:
    PORT_NUMBER = 8080
    OUTPUT = "/root/gps-data"

# Web Server
Twww = threading.Thread(name="W", target=web_server, args=(HOST_NAME, PORT_NUMBER))
Twww.start()

try:
    gps_logger_wrapper(OUTPUT)
except KeyboardInterrupt:
    DONE = True

Twww.join()
