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
SLEEP_TIME = 0.00001

# ATT Dictionary
ATT = {}

def do_json_output(self, output_dict):
    """ send back json text """
    output = json.dumps(output_dict).encode('utf-8')
    self.send_response(http.client.OK)
    self.send_header("Content-type", "application/json;charset=utf-8")
    self.send_header("Content-length", str(len(output)))
    self.end_headers()
    self.wfile.write(output)

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
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as temp:
        return float(temp.read())/1000

def imu_logger(output_directory):
    """ IMU Logger """
    global ATT
    cf_angle_x = cf_angle_y = cf_angle_z = 0

    config = util.read_config()

    # Open the output file
    with open(os.path.join(output_directory,datetime.datetime.now().strftime("%Y%m%d%H%M")+"_imu.csv"), "w") as imu_output:
        imu_output.write("%s %s %s *\n" % (config['time'], "VERSION", {"class": "VERSION", "version": util.DATA_API}))
        imu_output.write("%s %s %s *\n" % (config['time'], config['class'], json.dumps(config)))

        now = time.time()
        while not util.DONE:
            last_time = now
            now = time.time()
            acc = accel.get_axes()

            # Calibration
            acc['MAGx'] -= (MAX_MAG_X + MIN_MAG_X) / 2
            acc['MAGy'] -= (MAX_MAG_Y + MIN_MAG_Y) / 2
            acc['MAGz'] -= (MAX_MAG_Z + MIN_MAG_Z) / 2

            obj = {
                "class": "ATT",
                "device": accel.device(),
                "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "acc_x": acc['ACC'+config['imu']['x']],
                "acc_y": acc['ACC'+config['imu']['y']],
                "acc_z": acc['ACC'+config['imu']['z']],
                "gyro_x": acc['GYR'+config['imu']['x']],
                "gyro_y": acc['GYR'+config['imu']['y']],
                "gyro_z": acc['GYR'+config['imu']['z']],
                "mag_x": acc['MAG'+config['imu']['x']],
                "mag_y": acc['MAG'+config['imu']['y']],
                "mag_z": acc['MAG'+config['imu']['z']],
                "temp": _get_temp(),
            }

            delta_time = now - last_time

            # Calculate Yaw, Pitch and Roll with data fusion
            acc_x_angle = math.degrees(math.atan2(obj['acc_y'], obj['acc_z']))
            acc_y_angle = math.degrees(math.atan2(obj['acc_z'], obj['acc_x']))
            acc_z_angle = math.degrees(math.atan2(obj['acc_x'], obj['acc_y']))

            cf_angle_x = AA*(cf_angle_x+obj['gyro_x']*delta_time) + (1-AA)*acc_x_angle
            cf_angle_y = AA*(cf_angle_y+obj['gyro_y']*delta_time) + (1-AA)*acc_y_angle
            cf_angle_z = AA*(cf_angle_z+obj['gyro_z']*delta_time) + (1-AA)*acc_z_angle

            obj['pitch'] = cf_angle_x
            obj['pitch_st'] = "N"
            obj['roll'] = cf_angle_y - 90
            obj['roll_st'] = "N"
            obj['yaw'] = cf_angle_z
            obj['yaw_st'] = "N"

            # Calculate Heading
            obj['heading'] = (math.degrees(math.atan2(obj['mag_y'], obj['mag_x'])) - 90) % 360.0

            # Calculate vector length
            obj["acc_len"] = math.sqrt(obj['acc_x']**2+obj['acc_y']**2+obj['acc_z']**2)
            obj["mag_len"] = math.sqrt(obj['mag_x']**2+obj['mag_y']**2+obj['mag_z']**2)
            obj["mag_st"] = "N"

            # Log the output
            imu_output.write("%s %s %s *\n" % (obj['time'], obj['class'], json.dumps(obj)))
            ATT = obj

            # Delay Loop
            while (time.time() - now) < LOOP_DELAY:
                time.sleep(SLEEP_TIME)

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
