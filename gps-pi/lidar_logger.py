#!/usr/bin/python3
"""
LIDAR Logger
"""

import os
import sys
import threading
import time
import datetime
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

from rplidar import RPLidar

import util

LIDAR_STATUS = False
LIDAR_DATA = {}

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(s):
        """Respond to a GET request."""

        content_type = "text/html; charset=utf-8"

        if s.path == "/lidar":
            content_type = "application/json"
            output = json.dumps(LIDAR_DATA)
        elif s.path == "/lidar-stream":
            content_type = "text/event-stream"
            s.send_response(200)
            s.send_header("content-type", content_type)
            s.end_headers()
            while not util.DONE:
                try:
                    lines = [
                            "event: lidar\n",
                            "data: " + json.dumps(LIDAR_DATA) + "\n",
                            "\n",
                            ]
                    for line in lines:
                        s.wfile.write(line.encode('utf-8'))
                    time.sleep(util.STREAM_DELAY)
                except (BrokenPipeError, ConnectionResetError):
                    break
            return
        else:
            s.send_error(404, s.path)
            return

        s.send_response(200)
        s.send_header("Content-type", content_type)
        s.send_header("Content-length", str(len(output)))
        s.end_headers()
        s.wfile.write(output.encode('utf-8'))

def lidar_logger(output_directory):
    global LIDAR_STATUS, LIDAR_DATA

    port_name = '/dev/lidar'
    lidar = None

    # Configure
    config = util.read_config()

    while not util.DONE:
        try:
            lidar = RPLidar(port_name)
            print(lidar.get_info())
            print(lidar.get_health())
            # Open the output file
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
            with open(os.path.join(output_directory,timestamp+"_lidar.csv"), "w") as lidar_output:
                lidar_output.write("#v%d\n" % util.DATA_API)
                lidar_output.write("%s %s %s *\n" % (config['time'], config['class'], json.dumps(config)))
                for i, scan in enumerate(lidar.iter_scans(max_buf_meas=1500)):
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
                    if util.DONE:
                        break
        except KeyboardInterrupt:
            util.DONE = True
        except Exception as ex:
            print("LIDAR Logger Exception: %s" % ex)
            time.sleep(util.ERROR_DELAY)

        if lidar is not None:
            lidar.stop()
            lidar.stop_motor()
            lidar.disconnect()
        LIDAR_STATUS = False
        time.sleep(util.ERROR_DELAY)

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

if __name__ == "__main__":
    # Output Directory
    try:
        HOST_NAME = ''
        PORT_NUMBER = int(sys.argv[1])
        OUTPUT = sys.argv[2]
    except IndexError:
        PORT_NUMBER = 8082
        OUTPUT = "/root/gps-data"

    Twww = threading.Thread(name="W", target=web_server, args=(HOST_NAME, PORT_NUMBER, ThreadedHTTPServer, MyHandler))
    Twww.start()

    try:
        lidar_logger_wrapper(OUTPUT)
    except KeyboardInterrupt:
        util.DONE = True

    Twww.join()
