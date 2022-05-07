#!/usr/bin/python3
"""
GPS/IMU Logger for Wit-Motion JY-GPSIMU
"""

import os
import sys
import threading
import time
import datetime
import json
import statistics
import re
import math
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import http.client

import witmotionjygpsimu as gps
import nmea
import util


ALWAYS_LOG = True

ATT = TPV = SKY = {}
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

def handle_imu_stream(self, _groups, _qsdict):
    """ Stream IMU Data """
    self.send_response(http.client.OK)
    self.send_header("content-type", "text/event-stream")
    self.end_headers()
    while not util.DONE:
        try:
            lines = [
                "event: att\n",
                "data: " + json.dumps(ATT) + "\n",
                "\n",
            ]
            for line in lines:
                self.wfile.write(line.encode('utf-8'))
            time.sleep(util.STREAM_DELAY)
        except (BrokenPipeError, ConnectionResetError):
            break

def handle_imu(self, _groups, _qsdict):
    """ IMU Data """
    do_json_output(self, ATT)

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
    {
        "pattern": re.compile(r"GET /imu-stream$"),
        "handler": handle_imu_stream,
    },
    {
        "pattern": re.compile(r"GET /imu$"),
        "handler": handle_imu,
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

def _get_temp():
    """ Get Device Temperature """
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as temp:
            return float(temp.read())/1000
    except:
        return 0.0

def gpsimu_logger(output_directory):
    """ GPS Data Logger """
    global SKY, TPV, ATT
    global HOLD
    global GPS_NUM_SAT, GPS_NUM_USED

    hold_lat = []
    hold_lon = []
    hold_alt = []

    config = util.read_config()

    # Create the output directory
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    # Listen
    session = gps.WitMotionJyGpsImu("/dev/ttyUSB0")

    # Open the output file
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    with open(os.path.join(output_directory,timestamp+"_gps.csv"), "w") as gps_output, \
        open(os.path.join(output_directory,timestamp+"_imu.csv"), "w") as imu_output:

        gps_output.write("%s %s %s *\n" % (config['time'], "VERSION", {"class": "VERSION", "version": util.DATA_API}))
        gps_output.write("%s %s %s *\n" % (config['time'], config['class'], json.dumps(config)))

        imu_output.write("%s %s %s *\n" % (config['time'], "VERSION", {"class": "VERSION", "version": util.DATA_API}))
        imu_output.write("%s %s %s *\n" % (config['time'], config['class'], json.dumps(config)))

        while not util.DONE:
            # GPS
            report = session.next()
            # To see all report data, uncomment the line below
            #print(report)
            for lines in report:
                for timestamp, typeclass, obj in lines:
                    if typeclass == "SKY":
                        (GPS_NUM_USED, GPS_NUM_SAT) = nmea.calc_used(obj)
                        SKY = obj
                    elif typeclass == "TPV":
                        # Add Sat Metrics
                        obj['num_sat'] = GPS_NUM_SAT
                        obj['num_used'] = GPS_NUM_USED
                        obj['hold'] = HOLD
                        TPV = obj

                    # Log the Data
                    if 'time' in obj:
                        if typeclass == "ATT":
                            acc = obj
                            obj = {
                                "class": "ATT",
                                "device": acc['device'],
                                "time": acc['time'],
                                "acc_x": acc['ACC'+config['gpsimu']['x']],
                                "acc_y": acc['ACC'+config['gpsimu']['y']],
                                "acc_z": acc['ACC'+config['gpsimu']['z']],
                                "gyro_x": acc['GYR'+config['gpsimu']['x']],
                                "gyro_y": acc['GYR'+config['gpsimu']['y']],
                                "gyro_z": acc['GYR'+config['gpsimu']['z']],
                                "mag_x": acc['MAG'+config['gpsimu']['x']],
                                "mag_y": acc['MAG'+config['gpsimu']['y']],
                                "mag_z": acc['MAG'+config['gpsimu']['z']],
                                "pitch": acc['ANG'+config['gpsimu']['x']],
                                "pitch_st": "N",
                                "roll": acc['ANG'+config['gpsimu']['y']],
                                "roll_st": "N",
                                "yaw": acc['ANG'+config['gpsimu']['z']],
                                "yaw_st": "N",
                                "temp": acc['temp'],
                            }
                            # Calculate Heading
                            obj['heading'] = (math.degrees(math.atan2(obj['mag_y'], obj['mag_x'])) - 90) % 360.0

                            # Calculate vector length
                            obj["acc_len"] = math.sqrt(obj['acc_x']**2+obj['acc_y']**2+obj['acc_z']**2)
                            obj["mag_len"] = math.sqrt(obj['mag_x']**2+obj['mag_y']**2+obj['mag_z']**2)
                            obj["mag_st"] = "N"

                            imu_output.write("%s %s %s *\n" % (obj['time'], obj['class'], json.dumps(obj)))
                            ATT = obj
                        elif typeclass in ["TPV", "SKY"]:
                            gps_output.write("%s %s %s *\n" % (obj['time'], obj['class'], json.dumps(obj)))

                    # Short Circuit the rest of the checks
                    if HOLD == -1:
                        continue

                    if obj['class'] == 'TPV' and 'lat' in obj and 'lon' in obj and 'time' in obj:
                        if HOLD > 0:
                            hold_lat.append(obj['lat'])
                            hold_lon.append(obj['lon'])
                            if 'alt' in obj:
                                hold_alt.append(obj['alt'])
                            HOLD -= 1
                        elif HOLD == 0:
                            with open(os.path.join(output_directory,timestamp+"_marks.csv"), "a") as mark:
                                mark_obj = {
                                    "class": "MARK",
                                    "lat": statistics.mean(hold_lat),
                                    "lon": statistics.mean(hold_lon),
                                    "nSat": GPS_NUM_SAT,
                                    "uSat": GPS_NUM_USED,
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

def gpsimu_logger_wrapper(output_directory):
    """ Wrapper Around GPS Logger Function """

    try:
        gpsimu_logger(output_directory)
    except StopIteration:
        print("GPSIMU has terminated")
        util.DONE = True
    except Exception as ex:
        print("GPSIMU Logger Exception: %s" % ex)
    print("GPSIMU done")

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
        gpsimu_logger_wrapper(OUTPUT)
    except KeyboardInterrupt:
        util.DONE = True

    Twww.join()
