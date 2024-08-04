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
import re
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import http.client

import hps_3d_160_lidar as hps

import util

LIDAR_STATUS = False
LIDAR_DATA = {}

def do_json_output(self, output_dict):
    """ send back json text """
    output = json.dumps(output_dict).encode('utf-8')
    self.send_response(http.client.OK)
    self.send_header("Content-Type", "application/json;charset=utf-8")
    self.send_header("Content-Length", str(len(output)))
    self.end_headers()
    self.wfile.write(output)

def handle_lidar_stream(self, _groups, _qsdict):
    """ Stream LIDAR Data """
    self.send_response(http.client.OK)
    self.send_header("Content-Type", "text/event-stream")
    self.end_headers()
    try:
        while not util.DONE:
            output = "event: lidar\ndata: " + json.dumps(LIDAR_DATA) + "\n\n"
            self.wfile.write(output.encode('utf-8'))
            self.wfile.flush()
            time.sleep(util.STREAM_DELAY)
    except (BrokenPipeError, ConnectionResetError):
        pass

def handle_lidar(self, _groups, _qsdict):
    """ LIDAR Data """
    do_json_output(self, LIDAR_DATA)

MATCHES = [
    {
        "pattern": re.compile(r"GET /lidar/$"),
        "accept": "text/event-stream",
        "handler": handle_lidar_stream,
    },
    {
        "pattern": re.compile(r"GET /lidar/$"),
        "handler": handle_lidar,
    },
]

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    """ Web Handler """
    def do_GET(self):
        """Respond to a GET request."""
        url = urlparse(self.path)
        qsdict = parse_qs(url.query)

        for match in MATCHES:
            groups = match['pattern'].match(self.command + " " + url.path)
            if groups is not None:
                if 'accept' in match and match['accept'] != self.headers['Accept']:
                    continue
                match['handler'](self, groups, qsdict)
                return

        self.send_error(http.client.NOT_FOUND, self.path)

def lidar_logger(output_directory):
    """ LIDAR Logger """
    global LIDAR_STATUS, LIDAR_DATA

    lidar = None

    # Configure
    config = util.read_config()

    port_name = config['hpslidar'].get('serial', '/dev/ttyACM0')

    while not util.DONE:
        try:
            # Open the output file
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
            with open(os.path.join(output_directory,timestamp+"_lidar.csv"), "w") as lidar_output:
                util.write_header(lidar_output, config)
                lidar = hps.Hps3DLidar(config, port_name, 0, lidar_output)
                #print(lidar.read_version())
                #print(lidar.read_serial())

                while True:
                    lidar.set_working_mode(hps.Hps3DLidar.MODE_SINGLE)
                    time.sleep(util.STREAM_DELAY)
                    LIDAR_DATA = lidar.data
                    LIDAR_STATUS = True
                    if util.DONE:
                        break
        except KeyboardInterrupt:
            util.DONE = True
        except Exception as ex:
            print("LIDAR Logger Exception: %s" % ex)
            time.sleep(util.ERROR_DELAY)

        if lidar is not None:
            lidar.done()
        LIDAR_STATUS = False
        time.sleep(util.ERROR_DELAY)

def lidar_logger_wrapper(output_directory):
    """ Wrapper Around LIDAR Logger Function """
    global LIDAR_STATUS
    LIDAR_STATUS = False
    try:
        lidar_logger(output_directory)
    except TypeError as ex:
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

    Twww = threading.Thread(name="W", target=util.web_server, args=(HOST_NAME, PORT_NUMBER, ThreadedHTTPServer, MyHandler))
    Twww.start()

    try:
        lidar_logger_wrapper(OUTPUT)
    except KeyboardInterrupt:
        util.DONE = True

    Twww.join()
