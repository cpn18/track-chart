#!/usr/bin/python3
"""
IMU Logger
"""

import os
import sys
import threading
import time
import datetime
import json
import math
import re
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import http.client
import socket

import berryimu_shim as accel

import util

AA = 0.98

MAX_MAG_X = -7
MIN_MAG_X = -1525
MAX_MAG_Y = 1392
MIN_MAG_Y = 277
MAX_MAG_Z = -1045
MIN_MAG_Z = -1534

# Loop delay
LOOP_DELAY = 0.02

SAMPLES = 0

# ATT Dictionary
ATT = {}

CONFIG = {}

def send_udp(sock, ip, port, obj):
    """ Send Packet """
    sock.sendto(json.dumps(obj).encode(), (ip, port))

def do_json_output(self, output_dict):
    """ send back json text """
    output = json.dumps(output_dict).encode('utf-8')
    self.send_response(http.client.OK)
    self.send_header("Content-Type", "application/json;charset=utf-8")
    self.send_header("Content-Length", str(len(output)))
    self.end_headers()
    self.wfile.write(output)

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
    SAMPLES = 100
    do_json_output(self, {"message": "Zeroing IMU..."})

def handle_get(self, _groups, _qsdict):
    """ Get Module Status """
    output = json.dumps({"imu": CONFIG['imu']}).encode()
    self.send_response(http.client.OK)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(len(output)))
    self.end_headers()
    self.wfile.write(output)

def handle_put(self, _groups, _qsdict):
    """ Update Module Status """
    data = json.loads(self.rfile.read(int(self.headers['content-length'])))
    CONFIG['imu'].update(data)
    self.send_response(http.client.OK)
    self.send_header("Content-Length", "0")
    self.end_headers()

MATCHES = [
    {
        "pattern": re.compile(r"GET /imu/config$"),
        "handler": handle_get,
    },
    {
        "pattern": re.compile(r"PUT /imu/config$"),
        "handler": handle_put,
    },
    {
        "pattern": re.compile(r"GET /imu/zero$"),
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

    def def do_GET(self):
        self.handle_web_request()

    def do_PUT(self):
        self.handle_web_request()

def imu_logger(output_directory):
    """ IMU Logger """
    global ATT
    global SAMPLES

    saved_pitch = []
    saved_roll = []
    saved_yaw = []

    cf_angle_x = cf_angle_y = cf_angle_z = 0

    CONFIG.update(util.read_config())
    if 'logging' not in CONFIG['imu']:
        CONFIG['imu']['logging'] = True

    # UDP Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    

    if 'pitch_adj' not in CONFIG['imu']:
        CONFIG['imu']['pitch_adj'] = 0
    if 'roll_adj' not in CONFIG['imu']:
        CONFIG['imu']['roll_adj'] = 0
    if 'yaw_adj' not in CONFIG['imu']:
        CONFIG['imu']['yaw_adj'] = 0

    # Open the output file
    with open(os.path.join(output_directory,datetime.datetime.now().strftime("%Y%m%d%H%M")+"_imu.csv"), "w") as imu_output:
        util.write_header(imu_output, CONFIG)

        now = time.time()
        while not util.DONE:
            last_time = now
            now = time.time()
            delta_time = now - last_time

            acc = accel.get_axes()

            # Calibration
            acc['MAGx'] -= (MAX_MAG_X + MIN_MAG_X) / 2
            acc['MAGy'] -= (MAX_MAG_Y + MIN_MAG_Y) / 2
            acc['MAGz'] -= (MAX_MAG_Z + MIN_MAG_Z) / 2

            obj = {
                "class": "ATT",
                "device": accel.device(),
                "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "acc_x": acc['ACC'+CONFIG['imu']['x']],
                "acc_y": acc['ACC'+CONFIG['imu']['y']],
                "acc_z": acc['ACC'+CONFIG['imu']['z']],
                "gyro_x": acc['GYR'+CONFIG['imu']['x']],
                "gyro_y": acc['GYR'+CONFIG['imu']['y']],
                "gyro_z": acc['GYR'+CONFIG['imu']['z']],
                "mag_x": acc['MAG'+CONFIG['imu']['x']],
                "mag_y": acc['MAG'+CONFIG['imu']['y']],
                "mag_z": acc['MAG'+CONFIG['imu']['z']],
                "temp": util.get_cpu_temp(),
            }

            # Calculate Yaw, Pitch and Roll with data fusion
            acc_x_angle = math.degrees(math.atan2(obj['acc_y'], obj['acc_z']))
            acc_y_angle = math.degrees(math.atan2(obj['acc_z'], obj['acc_x']))
            acc_z_angle = math.degrees(math.atan2(obj['acc_x'], obj['acc_y']))

            cf_angle_x = AA*(cf_angle_x+obj['gyro_x']*delta_time) + (1-AA)*acc_x_angle
            cf_angle_y = AA*(cf_angle_y+obj['gyro_y']*delta_time) + (1-AA)*acc_y_angle
            cf_angle_z = AA*(cf_angle_z+obj['gyro_z']*delta_time) + (1-AA)*acc_z_angle

            obj['pitch'] = cf_angle_x + CONFIG['imu']['pitch_adj']
            obj['pitch_st'] = "N"
            obj['roll'] = cf_angle_y - 90 + CONFIG['imu']['roll_adj']
            obj['roll_st'] = "N"
            obj['yaw'] = cf_angle_z + CONFIG['imu']['yaw_adj']
            obj['yaw_st'] = "N"

            # Calculate Heading
            obj['heading'] = (math.degrees(math.atan2(obj['mag_y'], obj['mag_x'])) - 90) % 360.0

            # Calculate vector length
            obj["acc_len"] = math.sqrt(obj['acc_x']**2+obj['acc_y']**2+obj['acc_z']**2)
            obj["mag_len"] = math.sqrt(obj['mag_x']**2+obj['mag_y']**2+obj['mag_z']**2)
            obj["mag_st"] = "N"

            if SAMPLES > 0:
                saved_pitch.append(cf_angle_x)
                saved_roll.append(cf_angle_y - 90)
                saved_yaw.append(cf_angle_y)
                SAMPLES -= 1
            elif len(saved_pitch) > 0:
                CONFIG['imu']['pitch_adj'] = -sum(saved_pitch)/len(saved_pitch)
                CONFIG['imu']['roll_adj'] = -sum(saved_roll)/len(saved_roll)
                CONFIG['imu']['yaw_adj'] = -sum(saved_yaw)/len(saved_yaw)
                SAMPLES = 0
                saved_pitch = saved_roll = saved_yaw = []
                util.write_config(CONFIG)
                util.write_header(imu_output, CONFIG)

            # Log the output
            send_udp(sock, CONFIG['udp']['ip'], CONFIG['udp']['port'], obj)
            if CONFIG['imu']['logging']:
                imu_output.write("%s %s %s *\n" % (obj['time'], obj['class'], json.dumps(obj)))
                imu_output.flush()

            ATT = obj

            # Delay Loop
            sleep_time = now + LOOP_DELAY - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)

def imu_logger_wrapper(output_directory):
    """ Wrapper Around IMU Logger Function """

    print("IMU starting")
    try:
        imu_logger(output_directory)
    except Exception as ex:
        print("IMU Logger Exception: %s" % ex)
    print("IMU done")

# MAIN START

if __name__ == "__main__":
    # Command Line Configuration
    try:
        HOST_NAME = ''
        PORT_NUMBER = int(sys.argv[1])
        OUTPUT = sys.argv[2]
    except IndexError:
        PORT_NUMBER = 8081
        OUTPUT = "/root/gps-data"

    # Web Server
    Twww = threading.Thread(name="W", target=util.web_server, args=(HOST_NAME, PORT_NUMBER, ThreadedHTTPServer, MyHandler))
    Twww.start()

    try:
        imu_logger_wrapper(OUTPUT)
    except KeyboardInterrupt:
        util.DONE = True

    Twww.join()
