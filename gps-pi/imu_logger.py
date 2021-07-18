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
from socketserver import ThreadingMixIn

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

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(s):
        """Respond to a GET request."""
        global DONE

        content_type = "text/html; charset=utf-8"

        if s.path == "/imu":
            content_type = "application/json"
            output = json.dumps(ATT) + "\n"
        elif s.path == "/imu-stream":
            content_type = "text/event-stream"
            s.send_response(200)
            s.send_header("content-type", content_type)
            s.end_headers()
            while not DONE:
                lines = [
                    "event: att\n",
                    "data: " + json.dumps(ATT) + "\n",
                    "\n",
                ]
                for line in lines:
                    s.wfile.write(line.encode('utf-8'))
                time.sleep(5)
            return
        else:
            s.send_error(404, s.path)
            return

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

import time
import math
import datetime
import json
import os
import berryimu_shim as accel

AA = 0.98

MAX_MAG_X = -7
MIN_MAG_X = -1525
MAX_MAG_Y = 1392
MIN_MAG_Y = 277
MAX_MAG_Z = -1045
MIN_MAG_Z = -1534

# Insert delay if Exception occurs
ERROR_DELAY = 1

# Loop delay
LOOP_DELAY = 0.02

# Version
VERSION = 9

# Set to True to exit
DONE = False

ATT = {}

def _get_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as t:
        return float(t.read())/1000

def imu_logger(output_directory):
    """ IMU Logger """
    global ATT
    gyroXangle = gyroYangle = gyroZangle = 0
    CFangleX = CFangleY = CFangleZ = 0

    # Open the output file
    with open(os.path.join(output_directory,datetime.datetime.now().strftime("%Y%m%d%H%M")+"_imu.csv"), "w") as imu_output:
        imu_output.write("#v%d\n" % VERSION)
        imu_output.write("%s %s %s *\n" % (CONFIG['time'], CONFIG['class'], json.dumps(CONFIG)))

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
                 "acc_x": acc['ACC'+CONFIG['imu']['x']],
                 "acc_y": acc['ACC'+CONFIG['imu']['y']],
                 "acc_z": acc['ACC'+CONFIG['imu']['z']],
                 "gyro_x": acc['GYR'+CONFIG['imu']['x']],
                 "gyro_y": acc['GYR'+CONFIG['imu']['y']],
                 "gyro_z": acc['GYR'+CONFIG['imu']['z']],
                 "mag_x": acc['MAG'+CONFIG['imu']['x']],
                 "mag_y": acc['MAG'+CONFIG['imu']['y']],
                 "mag_z": acc['MAG'+CONFIG['imu']['z']],
                 "temp": _get_temp(),
             }

             DT = now - last_time

             # Calculate Angle From Gyro
             #gyroXangle += acc['GYRx'] * DT
             #gyroYangle += acc['GYRy'] * DT
             #gyroZangle += acc['GYRz'] * DT

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

             #print(json.dumps(obj))
             #print("AccLen %7.3f\tYaw %7.3f\tPitch %7.3f\tRoll %7.3f" % (obj['acc_len'],obj['yaw'], obj['pitch'], obj['roll']))
             #print("MagLen %7.3f\tMagX %d\tMagY %d\tMagZ %d\tMagHeading %7.3f" % (obj['mag_len'], obj['mag_x'], obj['mag_y'], obj['mag_z'], obj['heading']))

             # Delay Loop
             while (time.time() - now) < LOOP_DELAY:
                 time.sleep(LOOP_DELAY/2)

def imu_logger_wrapper(output_directory):
    """ Wrapper Around IMU Logger Function """
    global ACC_STATUS

    mylog("IMU starting")
    try:
        ACC_STATUS = True
        imu_logger(output_directory)
    except Exception as ex:
        mylog("IMU Logger Exception: %s" % ex)
    mylog("IMU done")
    ACC_STATUS = False

# MAIN START
INLOCSYNC = False
DONE = False
VERSION = 9
ATT = {}
TEMP = 0

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
    PORT_NUMBER = 8081
    OUTPUT = "/root/gps-data"

# Web Server
httpd = ThreadedHTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)

Twww = threading.Thread(name="W", target=web_server, args=(httpd,))
Twww.start()

try:
    imu_logger_wrapper(OUTPUT)
except KeyboardInterrupt:
    DONE = True
    pass

httpd.shutdown()
httpd.server_close()
Twww.join()
