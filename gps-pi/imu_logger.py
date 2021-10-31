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
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

import berryimu_shim as accel

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

# Set to True to exit
DONE = False

# ATT Dictionary
ATT = {}

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    """ Web Request Handler """
    def do_GET(self):
        """Respond to a GET request."""
        global DONE

        content_type = "text/html; charset=utf-8"

        if self.path == "/imu":
            content_type = "application/json"
            output = json.dumps(ATT) + "\n"
        elif self.path == "/imu-stream":
            content_type = "text/event-stream"
            self.send_response(200)
            self.send_header("content-type", content_type)
            self.end_headers()
            while not DONE:
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
            return
        else:
            self.send_error(404, self.path)
            return

        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.send_header("Content-length", str(len(output)))
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))

def _get_temp():
    """ Get Device Temperature """
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as temp:
        return float(temp.read())/1000

def imu_logger(output_directory):
    """ IMU Logger """
    global ATT
    gyroXangle = gyroYangle = gyroZangle = 0
    CFangleX = CFangleY = CFangleZ = 0

    config = util.read_config()

    # Open the output file
    with open(os.path.join(output_directory,datetime.datetime.now().strftime("%Y%m%d%H%M")+"_imu.csv"), "w") as imu_output:
        imu_output.write("#v%d\n" % util.DATA_API)
        imu_output.write("%s %s %s *\n" % (config['time'], config['class'], json.dumps(config)))

        now = time.time()
        while not DONE:
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

            DT = now - last_time

            # Calculate Yaw, Pitch and Roll with data fusion
            AccXangle = math.degrees(math.atan2(obj['acc_y'], obj['acc_z']))
            AccYangle = math.degrees(math.atan2(obj['acc_z'], obj['acc_x']))
            AccZangle = math.degrees(math.atan2(obj['acc_x'], obj['acc_y']))

            CFangleX = AA*(CFangleX+obj['gyro_x']*DT) + (1-AA)*AccXangle
            CFangleY = AA*(CFangleY+obj['gyro_y']*DT) + (1-AA)*AccYangle
            CFangleZ = AA*(CFangleZ+obj['gyro_z']*DT) + (1-AA)*AccZangle

            obj['pitch'] = CFangleX
            obj['pitch_st'] = "N"
            obj['roll'] = CFangleY - 90
            obj['roll_st'] = "N"
            obj['yaw'] = CFangleZ
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
    Twww = threading.Thread(name="W", target=util.web_server, args=(HOST_NAME, PORT_NUMBER))
    Twww.start()

    try:
        imu_logger_wrapper(OUTPUT)
    except KeyboardInterrupt:
        DONE = True

    Twww.join()
