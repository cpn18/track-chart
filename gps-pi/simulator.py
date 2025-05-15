#!/usr/bin/python3
"""
Simulator
"""

import os
import sys
import threading
import time
from datetime import datetime
import json
import re
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import http.client
import socket

import util

def send_udp(sock, ip_addr, port, obj):
    """ Send Packet """
    sock.sendto(json.dumps(obj).encode(), (ip_addr, port))

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
    pass

MATCHES = [
    {
        "pattern": re.compile(r"GET /sim/log$"),
        "handler": handle_log,
    },
    {
        "pattern": re.compile(r"PUT /sim/log$"),
        "handler": handle_log,
    }
]

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    """ Web Request Handler """

    def handle_web_request(self):
        """Respond to a request."""
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

    def do_GET(self):
        self.handle_web_request()

    def do_PUT(self):
        self.handle_web_request()

def simulator(output_directory):
    """ Read JSON data line by line and stream packets in real time."""

    config = util.read_config()

    # UDP Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Check for the simulator input
    filename = config['sim']['data']
    if not os.path.isfile(filename):
        raise FileNotFoundError

    if not os.access(filename, os.R_OK):
        raise PermissionError

    # Create the output directory
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    output = os.path.join(
        output_directory,
        datetime.now().strftime("%Y%m%d%H%M") + "_sim.csv"
    )

    # Open the output file
    with open(output, "w") as sim_output:
        util.write_header(sim_output, config)

        while not util.DONE:

            print(f"Reading from {filename}")
            with open(filename, 'r') as sim_input:
                first = True

                # Now iterate through every line/packet
                for line in sim_input:
                    obj = json.loads(line)
                    packet_time = util.parse_time(obj['time'])

                    if first:
                        # Parse the first line to determine the initial_time
                        initial_time = packet_time
                        simulation_start = time.time()
                        first = False

                    offset = (packet_time - initial_time).total_seconds()
                    now_offset = time.time() - simulation_start
                    sleep_time = offset - now_offset
                    if sleep_time > 0:
                        time.sleep(sleep_time)

                    # Send the Data
                    send_udp(sock, config['udp']['ip'], config['udp']['port'], obj)
                    if config['sim']['logging']:
                        sim_output.write("%s %s %s *\n" % (obj['time'], obj['class'], json.dumps(obj)))
                        sim_output.flush()

            # Pause, then restart data file
            print("Pausing...")
            time.sleep(60)

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
        PORT_NUMBER = 8084
        OUTPUT = "/root/gps-data"

    # Web Server
    Twww = threading.Thread(name="W", target=util.web_server, args=(HOST_NAME, PORT_NUMBER, ThreadedHTTPServer, MyHandler))
    Twww.start()

    try:
        simulator_wrapper(OUTPUT)
    except KeyboardInterrupt:
        util.DONE = True

    Twww.join()
