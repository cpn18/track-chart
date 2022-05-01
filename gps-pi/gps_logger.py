#!/usr/bin/python3
"""
GPS Logger
"""

import os
import sys
import threading
import time
import datetime
import json
import statistics
import re
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import http.client

import gps
import nmea
import util

ALWAYS_LOG = True

TPV = SKY = {}
HOLD = -1
MEMO = ""

GPS_NUM_SAT = 0
GPS_NUM_USED = 0

def do_json_output(self, output_dict):
    """ send back json text """
    output = json.dumps(output_dict).encode('utf-8')
    self.send_response(http.client.OK)
    self.send_header("Content-type", "application/json;charset=utf-8")
    self.send_header("Content-length", str(len(output)))
    self.end_headers()
    self.wfile.write(output)

def handle_mark(self, _groups, qsdict):
    """ mark a location """
    global HOLD, MEMO
    HOLD = 1
    MEMO = qsdict['memo']
    do_json_output(self, {"message": "Marked..."})

def handle_hold(self, _groups, qsdict):
    """ hold a location """
    global HOLD, MEMO
    HOLD = 15
    MEMO = qsdict['memo']
    do_json_output(self, {"message": "Holding..."})

def handle_tpv(self, _groups, _qsdict):
    """ get a TPV report """
    do_json_output(self, TPV)

def handle_sky(self, _groups, _qsdict):
    """ get a SKY report """
    do_json_output(self, SKY)

def handle_gps_stream(self, _groups, _qsdict):
    """ Stream GPS Response """
    self.send_response(http.client.OK)
    self.send_header("Content-type", "text/event-stream")
    self.end_headers()
    while not util.DONE:
        try:
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
            time.sleep(util.STREAM_DELAY)
        except (BrokenPipeError, ConnectionResetError):
            break

def handle_gps(self, _groups, _qsdict):
    """ Single GPS """
    if TPV['time'] < SKY['time']:
        do_json_output(self, [TPV, SKY])
    else:
        do_json_output(self, [SKY, TPV])

MATCHES = [
    {
        "pattern": re.compile(r"GET /mark$"),
        "handler": handle_mark,
    },
    {
        "pattern": re.compile(r"GET /hold$"),
        "handler": handle_hold,
    },
    {
        "pattern": re.compile(r"GET /tpv$"),
        "handler": handle_tpv,
    },
    {
        "pattern": re.compile(r"GET /sky$"),
        "handler": handle_sky,
    },
    {
        "pattern": re.compile(r"GET /gps-stream$"),
        "handler": handle_gps_stream,
    },
    {
        "pattern": re.compile(r"GET /gps$"),
        "handler": handle_gps,
    },
]

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    """ Web Request Handler """

    def do_GET(self):
        """Respond to a GET request."""
        url = urlparse(self.path)
        qsdict = parse_qs(url.query)

        for match in MATCHES:
            groups = match['pattern'].match(self.command + " " + url.path)
            if groups is not None:
                match['handler'](self, groups, qsdict)
                return

        self.send_error(http.client.NOT_FOUND, self.path)

def gps_logger(output_directory):
    """ GPS Data Logger """
    global SKY, TPV
    global HOLD
    global GPS_NUM_SAT, GPS_NUM_USED

    hold_lat = []
    hold_lon = []
    hold_alt = []

    config = util.read_config()

    # Create the output directory
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    # Listen on port 2947 (gpsd) of localhost
    session = gps.gps(mode=gps.WATCH_ENABLE)

    # Open the output file
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    with open(os.path.join(output_directory,timestamp+"_gps.csv"), "w") as gps_output:
        gps_output.write("#v%d\n" % util.DATA_API)
        gps_output.write("%s %s %s *\n" % (config['time'], config['class'], json.dumps(config)))

        while not util.DONE:
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

            # Short Circuit the rest of the checks
            if HOLD == -1:
                continue

            if obj['class'] == 'TPV' and 'lat' in obj and 'lon' in obj and 'time' in obj:
                if HOLD > 0:
                    hold_lat.append(report.lat)
                    hold_lon.append(report.lon)
                    if 'alt' in report:
                        hold_alt.append(report.alt)
                    HOLD -= 1
                elif HOLD == 0:
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

def gps_logger_wrapper(output_directory):
    """ Wrapper Around GPS Logger Function """

    try:
        gps_logger(output_directory)
    except StopIteration:
        print("GPSD has terminated")
        util.DONE = True
    except Exception as ex:
        print("GPS Logger Exception: %s" % ex)
    print("GPS done")

# MAIN START

if __name__ == "__main__":
    # Command Line Configuration
    try:
        HOST_NAME = ''
        PORT_NUMBER = int(sys.argv[1])
        OUTPUT = sys.argv[2]
    except IndexError:
        PORT_NUMBER = 8080
        OUTPUT = "/root/gps-data"

    # Web Server
    Twww = threading.Thread(name="W", target=util.web_server, args=(HOST_NAME, PORT_NUMBER, ThreadedHTTPServer, MyHandler))
    Twww.start()

    try:
        gps_logger_wrapper(OUTPUT)
    except KeyboardInterrupt:
        util.DONE = True

    Twww.join()
