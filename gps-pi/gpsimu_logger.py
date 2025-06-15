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
import geo
from gps_common import update_odometer


ALWAYS_LOG = True

ATT = TPV = SKY = {}
TPV_SYS_TIME = SKY_SYS_TIME = 0
HOLD = -1
MEMO = ""
SAMPLES = 0

GPS_NUM_SAT = 0
GPS_NUM_USED = 0

ODOMETER = 0.0
ODIR = 1

CONFIG = {}

def do_json_output(self, output_dict):
    """ send back json text """
    output = json.dumps(output_dict).encode('utf-8')
    self.send_response(http.client.OK)
    self.send_header("Content-Type", "application/json;charset=utf-8")
    self.send_header("Content-Length", str(len(output)))
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

def handle_reset(self, _groups, qsdict):
    """ Reset Odometer """
    global ODOMETER
    try:
        ODOMETER = float(qsdict['mileage'][0])
    except (KeyError,ValueError):
        ODOMETER = 0.0
    do_json_output(self, {"message": "Reset Odometer..."})

def handle_reverse(self, _groups, _qsdict):
    """ Reset Odometer """
    global ODIR
    ODIR = -ODIR
    do_json_output(self, {"message": "Reverse Odometer..."})

def handle_tpv(self, _groups, _qsdict):
    """ get a TPV report """
    do_json_output(self, TPV)

def handle_sky(self, _groups, _qsdict):
    """ get a SKY report """
    do_json_output(self, SKY)

def handle_gps_stream(self, _groups, _qsdict):
    """ Stream GPS Response """
    self.send_response(http.client.OK)
    self.send_header("Content-Type", "text/event-stream")
    self.end_headers()
    try:
        while not util.DONE:
            if TPV_SYS_TIME < SKY_SYS_TIME:
                output = "event: tpv\ndata: " + json.dumps(TPV) + "\n\nevent: sky\ndata: " + json.dumps(SKY) + "\n\n"
            else:
                output = "event: sky\ndata: " + json.dumps(SKY) + "\n\nevent: tpv\ndata: " + json.dumps(TPV) + "\n\n"
            self.wfile.write(output.encode('utf-8'))
            self.wfile.flush()
            time.sleep(util.STREAM_DELAY)
    except (BrokenPipeError, ConnectionResetError):
        pass

def handle_gps(self, _groups, _qsdict):
    """ Single GPS """
    if TPV_SYS_TIME < SKY_SYS_TIME:
        do_json_output(self, [TPV, SKY])
    else:
        do_json_output(self, [SKY, TPV])

def handle_imu_stream(self, _groups, _qsdict):
    """ Stream IMU Data """
    self.send_response(http.client.OK)
    self.send_header("Content-Type", "text/event-stream")
    self.end_headers()
    try:
        while not util.DONE:
            output = "event: att\ndata: " + json.dumps(ATT) + "\n\n"
            self.wfile.write(output.encode('utf-8'))
            self.wfile.flush()
            time.sleep(util.STREAM_DELAY)
    except (BrokenPipeError, ConnectionResetError):
        pass

def handle_imu(self, _groups, _qsdict):
    """ IMU Data """
    do_json_output(self, ATT)

def handle_zero(self, _groups, _qsdict):
    """ Zero the IMU """
    global SAMPLES
    SAMPLES = 15
    do_json_output(self, {"message": "Zeroing IMU..."})

def handle_get(self, _groups, _qsdict):
    """ Get Module Status """
    output = json.dumps({"gps": CONFIG['gps'], "imu": CONFIG['imu']}).encode()
    self.send_response(http.client.OK)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(len(output)))
    self.end_headers()
    self.wfile.write(output)

def handle_put(self, _groups, _qsdict):
    """ Update Module Status """
    data = json.loads(self.rfile.read(int(self.headers['content-length'])))
    CONFIG['gps'].update(data['gps'])
    CONFIG['imu'].update(data['imu'])
    self.send_response(http.client.OK)
    self.send_header("Content-Length", "0")
    self.end_headers()

MATCHES = [
    {
        "pattern": re.compile(r"GET /gps/config$"),
        "handler": handle_get,
    },
    {
        "pattern": re.compile(r"PUT /gps/config$"),
        "handler": handle_put,
    },

    {
        "pattern": re.compile(r"GET /gps/mark$"),
        "handler": handle_mark,
    },
    {
        "pattern": re.compile(r"GET /gps/hold$"),
        "handler": handle_hold,
    },
        {
        "pattern": re.compile(r"GET /gps/odometer-reset$"),
        "handler": handle_reset,
    },
    {
        "pattern": re.compile(r"GET /gps/odometer-reverse$"),
        "handler": handle_reverse,
    },
    {
        "pattern": re.compile(r"GET /gps/tpv$"),
        "handler": handle_tpv,
    },
    {
        "pattern": re.compile(r"GET /gps/sky$"),
        "handler": handle_sky,
    },
    {
        "pattern": re.compile(r"GET /gps/$"),
        "accept": "text/event-stream",
        "handler": handle_gps_stream,
    },
    {
        "pattern": re.compile(r"GET /gps/$"),
        "handler": handle_gps,
    },
    {
        "pattern": re.compile(r"PUT /imu/zero$"),
        "handler": handle_zero,
    },
    {
        "pattern": re.compile(r"GET /imu/att$"),
        "handler": handle_imu,
    },
    {
        "pattern": re.compile(r"GET /imu/$"),
        "accept": "text/event-stream",
        "handler": handle_imu_stream,
    },
    {
        "pattern": re.compile(r"GET /imu/$"),
        "handler": handle_imu,
    },
]

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    """ Web Request Handler """

    def handle_web_request(self):
        """Respond to a GET request."""
        url = urlparse(self.path)
        qsdict = parse_qs(url.query)

        for match in MATCHES:
            groups = match['pattern'].match(self.command + " " + url.path)
            if groups is not None:
                if 'accept' in match and match['accept'] != self.headers['Accept']:
                    continue
                try:
                    match['handler'](self, groups, qsdict)
                except BrokenPipeError:
                    pass
                return

        self.send_error(http.client.NOT_FOUND, self.path)

    def do_GET(self):
        self.handle_web_request()

    def do_PUT(self):
        self.handle_web_request()

def gpsimu_logger(output_directory):
    """ GPS Data Logger """
    global SKY, TPV, SKY_SYS_TIME, TPV_SYS_TIME
    global HOLD
    global GPS_NUM_SAT, GPS_NUM_USED
    global ODOMETER
    global ATT
    global SAMPLES

    saved_pitch = []
    saved_roll = []
    saved_yaw = []

    last_pos = {}

    hold_lat = []
    hold_lon = []
    hold_alt = []

    CONFIG.update(util.read_config())

    if 'logging' not in CONFIG['gps']:
        CONFIG['gps']['logging'] = True
    if 'logging' not in CONFIG['imu']:
        CONFIG['imu']['logging'] = True

    if 'pitch_adj' not in CONFIG['imu']:
        CONFIG['imu']['pitch_adj'] = 0
    if 'roll_adj' not in CONFIG['imu']:
        CONFIG['imu']['roll_adj'] = 0
    if 'yaw_adj' not in CONFIG['imu']:
        CONFIG['imu']['yaw_adj'] = 0

    # Create the output directory
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    # Open the output file
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    with open(os.path.join(output_directory,timestamp+"_gps.csv"), "w") as gps_output, \
        open(os.path.join(output_directory,timestamp+"_imu.csv"), "w") as imu_output:

        util.write_header(gps_output, CONFIG)
        util.write_header(imu_output, CONFIG)

        # Listen
        session = gps.WitMotionJyGpsImu(
            CONFIG['gps']['serial'],
            gps_output, imu_output, CONFIG
        )

        while not util.DONE:
            time.sleep(1)

            SKY = session.get_sky()
            (GPS_NUM_USED, GPS_NUM_SAT) = nmea.calc_used(SKY)
            SKY_SYS_TIME = time.time()
            TPV = session.get_tpv()
            ATT = session.get_att()
            # Update Odometer
            ODOMETER, last_pos = update_odometer(
                ODOMETER,
                ODIR,
                last_pos,
                TPV
            )
            TPV['num_sat'] = GPS_NUM_SAT
            TPV['num_used'] = GPS_NUM_USED
            TPV['hold'] = HOLD
            TPV['odometer'] = ODOMETER
            TPV['odir'] = ODIR
            TPV_SYS_TIME = time.time()

            if SAMPLES > 0:
                saved_pitch.append(ATT['pitch'])
                saved_roll.append(ATT['roll'])
                saved_yaw.append(ATT['yaw'])
                SAMPLES -= 1
            elif len(saved_pitch) > 0:
                COMFIG['imu']['pitch_adj'] = -sum(saved_pitch)/len(saved_pitch)
                COMFIG['imu']['roll_adj'] = -sum(saved_roll)/len(saved_roll)
                COMFIG['imu']['yaw_adj'] = -sum(saved_yaw)/len(saved_yaw)
                SAMPLES = 0
                saved_pitch = saved_roll = saved_yaw = []
                util.write_config(COMFIG)
                util.write_header(imu_output, COMFIG)
                session.update_config(COMFIG)
                os._exit(0)

            # Short Circuit the rest of the checks
            if HOLD == -1:
                continue

            if 'lat' in TPV and 'lon' in TPV and 'time' in TPV:
                if HOLD > 0:
                    hold_lat.append(TPV['lat'])
                    hold_lon.append(TPV['lon'])
                    if 'alt' in TPV:
                        hold_alt.append(TPV['alt'])
                    HOLD -= 1
                elif HOLD == 0:
                    with open(os.path.join(output_directory,timestamp+"_marks.csv"),"a") as mark:
                        mark_obj = {
                            "class": "MARK",
                            "lat": statistics.mean(hold_lat),
                            "lon": statistics.mean(hold_lon),
                            "nSat": GPS_NUM_SAT,
                            "uSat": GPS_NUM_USED,
                            "time": TPV['time'],
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
