#!/usr/bin/python3
"""
LIDAR Logger
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
from socketserver import ThreadingMixIn

from rplidar import RPLidar

HOST_NAME = ''
PORT_NUMBER = 80

ALWAYS_LOG = True

ERROR_DELAY = 10
SYNC_DELAY = 5
IDLE_DELAY = 60

STREAM_DELAY = 1

def read_config():
    # Configure Axis
    try:
        with open("config.json", "r") as f:
            config = json.loads(f.read())
    except:
        config = {
            "imu": {"log": True, "x": "x", "y": "y", "z": "z"},
            "gps": {"log": True},
            "lidar": {"log": True},
            "audio": {"log": True},
        }

    config['class'] = "CONFIG"
    config['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return config

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(s):
        """Respond to a GET request."""
        global CURRENT
        global DONE
        global RESTART
        global HOLD
        global MEMO

        content_type = "text/html; charset=utf-8"

        if s.path == "/lidar":
            content_type = "application/json"
            output = json.dumps(LIDAR_DATA)
        elif s.path == "/lidar-stream":
            content_type = "text/event-stream"
            s.send_response(200)
            s.send_header("content-type", content_type)
            s.end_headers()
            while not DONE:
                lines = [
                        "event: lidar\n",
                        "data: " + json.dumps(LIDAR_DATA) + "\n",
                        "\n",
                        ]
                for line in lines:
                    s.wfile.write(line.encode('utf-8'))
                time.sleep(STREAM_DELAY)
            return
        else:
            s.send_error(404, s.path)
            return

        s.send_response(200)
        s.send_header("Content-type", content_type)
        s.send_header("Content-length", str(len(output)))
        s.end_headers()
        s.wfile.write(output.encode('utf-8'))

def web_server(host_name, port_number):
    global DONE
    # Web Server
    httpd = ThreadedHTTPServer((host_name, port_number), MyHandler)
    while not DONE:
        try:
            print(time.asctime(), "Server Starts - %s:%s" % (host_name, port_number))
            httpd.serve_forever()
            print(time.asctime(), "Server Stops - %s:%s" % (host_name, port_number))
        except KeyboardInterrupt:
            DONE = True
        except Exception as ex:
            print(ex)
    httpd.shutdown()
    httpd.server_close()

def lidar_logger(output_directory):
    global DONE, LIDAR_STATUS, LIDAR_DATA

    port_name = '/dev/lidar'
    lidar = None

    # Configure
    config = read_config()

    while not DONE:
        try:
            lidar = RPLidar(port_name)
            print(lidar.get_info())
            print(lidar.get_health())
            # Open the output file
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
            with open(os.path.join(output_directory,timestamp+"_lidar.csv"), "w") as lidar_output:
                lidar_output.write("#v%d\n" % VERSION)
                lidar_output.write("%s %s %s *\n" % (config['time'], config['class'], json.dumps(config)))
                for i, scan in enumerate(lidar.iter_scans(max_buf_meas=1500)):
                    if INLOCSYNC or ALWAYS_LOG:
                        lidartime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                        data = []
                        for (_, angle, distance) in scan:
                            if distance > 0:
                                data.append((int(angle)%360, int(distance)))
                        lidar_data = {
                            'class': 'LIDAR',
                            'device': 'A1M8',
                            'time': lidartime,
                            'scan': data,
                        }
                        lidar_output.write("%s %s %s *\n" % (lidar_data['time'], lidar_data['class'], json.dumps(lidar_data)))
                        LIDAR_DATA = lidar_data
                    LIDAR_STATUS = True
                    if DONE:
                        break
        except KeyboardInterrupt:
            DONE = True
        except Exception as ex:
            print("LIDAR Logger Exception: %s" % ex)
            time.sleep(ERROR_DELAY)

        if lidar is not None:
            lidar.stop()
            lidar.stop_motor()
            lidar.disconnect()
        LIDAR_STATUS = False
        time.sleep(ERROR_DELAY)


def lidar_logger_wrapper(output_directory):
    """ Wrapper Around LIDAR Logger Function """
    global LIDAR_STATUS
    LIDAR_STATUS = False
    try:
        lidar_logger(output_directory)
    except Exception as ex:
        print("LIDAR Logger Exception: %s" % ex)
    LIDAR_STATUS = False
    print("LIDAR Done")

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

# Output Directory
try:
    PORT_NUMBER = int(sys.argv[1])
    OUTPUT = sys.argv[2]
except IndexError:
    PORT_NUMBER = 8082
    OUTPUT = "/root/gps-data"

Twww = threading.Thread(name="W", target=web_server, args=(HOST_NAME, PORT_NUMBER))
Twww.start()

lidar_logger_wrapper(OUTPUT)

Twww.join()
