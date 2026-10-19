#!/usr/bin/env python3
"""
Image Logger
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
import socket
import cv2

import util

# Loop delay
LOOP_DELAY = 1.0 # second

# IMAGE Dictionary
IMAGE = {}

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

def handle_camera_stream(self, _groups, _qsdict):
    """ Stream IMU Data """
    self.send_response(http.client.OK)
    self.send_header("Content-Type", "text/event-stream")
    self.end_headers()
    try:
        while not util.DONE:
            output = "event: image\ndata: " + json.dumps(IMAGE) + "\n\n"
            self.wfile.write(output.encode('utf-8'))
            self.wfile.flush()
            time.sleep(util.STREAM_DELAY)
    except (BrokenPipeError, ConnectionResetError):
        pass

def handle_camera(self, _groups, _qsdict):
    """ Image Data """
    do_json_output(self, IMAGE)

def handle_get(self, _groups, _qsdict):
    """ Get Module Status """
    output = json.dumps({"camera": CONFIG['camera']}).encode()
    self.send_response(http.client.OK)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(len(output)))
    self.end_headers()
    self.wfile.write(output)

def handle_put(self, _groups, _qsdict):
    """ Update Module Status """
    data = json.loads(self.rfile.read(int(self.headers['content-length'])))
    CONFIG['camera'].update(data['camera'])
    self.send_response(http.client.OK)
    self.send_header("Content-Length", "0")
    self.end_headers()

MATCHES = [
    {
        "pattern": re.compile(r"GET /camera/config$"),
        "handler": handle_get,
    },
    {
        "pattern": re.compile(r"PUT /camera/config$"),
        "handler": handle_put,
    },
    {
        "pattern": re.compile(r"GET /camera/image$"),
        "handler": handle_camera,
    },
    {
        "pattern": re.compile(r"GET /camera/$"),
        "accept": "text/event-stream",
        "handler": handle_camera_stream,
    },
    {
        "pattern": re.compile(r"GET /camera/$"),
        "handler": handle_camera,
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

def camera_logger(output_directory):
    """ IMU Logger """
    global IMAGE

    CONFIG.update(util.read_config())
    if 'logging' not in CONFIG['camera']:
        CONFIG['camera']['logging'] = True

    # Camera setup
    # 0 opens the default built-in webcam. Use 1, 2, etc., for external USB cameras.
    cap = cv2.VideoCapture(1)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    image_dir = output_directory + "/images/"

    # UDP Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    

    # Open the output file
    with open(os.path.join(output_directory,datetime.datetime.now().strftime("%Y%m%d%H%M")+"_camera.csv"), "w") as camera_output:
        util.write_header(camera_output, CONFIG)

        while not util.DONE:
            next_time = time.time() + LOOP_DELAY

            # Capture frame-by-frame
            # ret is a boolean (True if frame grabbed successfully), frame is the image array
            ret, frame = cap.read()
            if not ret:
                print("Error: Can't receive frame (stream end?). Exiting...")
                break

            timestamp = datetime.datetime.now()
            filename = timestamp.strftime("%Y%m%d_%H%M%S") + ".png"

            cv2.imwrite(image_dir + filename, frame)

            obj = {
                "class": "IMAGE",
                "device": "",
                "time": timestamp.isoformat(),
                "filename": filename
            }

            # Log the output
            send_udp(sock, CONFIG['analyzer']['udp']['host'], CONFIG['analyzer']['udp']['port'], obj)
            if CONFIG['camera']['logging']:
                camera_output.write("%s %s %s *\n" % (obj['time'], obj['class'], json.dumps(obj)))
                camera_output.flush()

            IMAGE = obj

            # Delay Loop
            sleep_time = next_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)

    # Always release the capture and destroy windows when done to free up hardware
    cap.release()
    cv2.destroyAllWindows()

def camera_logger_wrapper(output_directory):
    """ Wrapper Around IMU Logger Function """

    print("Camera starting")
    try:
        camera_logger(output_directory)
    except Exception as ex:
        print("Camera Logger Exception: %s" % ex)
    print("Camera done")

# MAIN START

if __name__ == "__main__":
    # Command Line Configuration
    try:
        HOST_NAME = ''
        PORT_NUMBER = int(sys.argv[1])
        OUTPUT = sys.argv[2]
    except IndexError:
        PORT_NUMBER = 8084
        OUTPUT = "/root/gps-data"

    # Web Server
    Twww = threading.Thread(name="W", target=util.web_server, args=(HOST_NAME, PORT_NUMBER, ThreadedHTTPServer, MyHandler))
    Twww.start()

    try:
        camera_logger_wrapper(OUTPUT)
    except KeyboardInterrupt:
        util.DONE = True

    Twww.join()
