#!/usr/bin/python3
"""
Simulator
"""

import os
import sys
import threading
import time
import datetime
import json
import statistics
import re
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import http.client
import socket

import gps
import nmea
import util
import geo

from gps_common import update_odometer

ALWAYS_LOG = True

TPV = SKY = {}
TPV_SYS_TIME = SKY_SYS_TIME = 0
HOLD = -1
MEMO = ""

GPS_NUM_SAT = 0
GPS_NUM_USED = 0

ODOMETER = 0.0
ODIR = 1

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


def handle_log(self, _groups, _qsdict):
    """ Turn Logging On/Off """
    global LOGGING

    LOGGING = False

MATCHES = [
    {
        "pattern": re.compile(r"GET /sim/log$"),
        "handler": handle_log,
    }
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
                if 'accept' in match and match['accept'] != self.headers['Accept']:
                    continue
                match['handler'](self, groups, qsdict)
                return

        self.send_error(http.client.NOT_FOUND, self.path)

def simulator(output_directory):
    """ Simulate reading JSON data line by line and streaming packets in real time."""

    config = util.read_config()

    # UDP Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Create the output directory
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    # Open the output file
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    with open(os.path.join(output_directory,timestamp+"_sim.csv"), "w") as sim_output:
        util.write_header(sim_output, config)

        with open(config['sim']['data'], 'r') as f:
            lines = f.read().splitlines()  # read file into a list of lines

        if not lines:
            return

        while not util.DONE:
            # Parse the first line to determine the initial_time
            first_packet = json.loads(lines[0])
            initial_time = parse_time(first_packet['time'])
            simulation_start = time.time()

            # Now iterate through every line/packet
            for line in lines:
                obj = json.loads(line)
                packet_time = parse_time(obj['time'])
                offset = (packet_time - initial_time).total_seconds()
                now_offset = time.time() - simulation_start
                sleep_time = offset - now_offset
                if sleep_time > 0:
                    time.sleep(sleep_time)

                # Send the Data
                send_udp(sock, config['udp']['ip'], config['udp']['port'], obj)
                if LOGGING:
                    sim_output.write("%s %s %s *\n" % (obj['time'], obj['class'], json.dumps(obj)))
                    sim_output.flush()


def simulator_wrapper(output_directory):
    """ Wrapper Around GPS Logger Function """

    try:
        simulator(output_directory)
    except Exception as ex:
        print("Simulator Exception: %s" % repr(ex))
        util.DONE = True
    print("Simulator done")

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
        simulator_wrapper(OUTPUT)
    except KeyboardInterrupt:
        util.DONE = True

    Twww.join()
