#!/usr/bin/python3
"""
LPCM Logger
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

import util

LPCM_DATA = {}

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

def handle_lpcm_stream(self, _groups, _qsdict):
    """ Stream LPCM """
    self.send_response(http.client.OK)
    self.send_header("Content-Type", "text/event-stream")
    self.end_headers()
    try:
        while not util.DONE:
            output = "event: lpcm\ndata: " + json.dumps(LPCM_DATA) + "\n\n"
            self.wfile.write(output.encode('utf-8'))
            self.wfile.flush()
            time.sleep(util.STREAM_DELAY)
    except (BrokenPipeError, ConnectionResetError):
        pass

def handle_lpcm(self, _groups, _qsdict):
    """ Single LPCM """
    do_json_output(self, LPCM_DATA)

MATCHES = [
    {
        "pattern": re.compile(r"GET /lpcm/$"),
        "accept": "text/event-stream",
        "handler": handle_lpcm_stream,
    },
    {
        "pattern": re.compile(r"GET /lpcm/$"),
        "handler": handle_lpcm,
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
                if 'accept' in match and match['accept'] != self.headers['Accept']:
                    continue
                match['handler'](self, groups, qsdict)
                return

        self.send_error(http.client.NOT_FOUND, self.path)

def lpcm_logger(output_directory):
    """ LPCM Capture Wrapper """
    global LPCM_DATA

    # Configure
    config = util.read_config()

    # UDP Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    with open(os.path.join(output_directory,timestamp+"_lpcm.csv"), "w") as lpcm_output:
        util.write_header(lpcm_output, config)
        while not util.DONE:
            try:
                timestamp = datetime.datetime.now()
                filename = timestamp.strftime("%Y%m%d%H%M")
                LPCM_DATA = {
                    "class": "LPCM",
                    "time": timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }

                if os.system("./lpcm_collect.sh %s %s \"%s\"" % (output_directory, filename, config['lpcm']['arecord'])) != 0:
                    time.sleep(util.ERROR_DELAY)
                else:
                    # Check if output files exist
                    for channel in ["left", "right", "stereo"]:
                        capture_file = filename+"_"+channel+".wav"
                        if os.path.isfile(os.path.join(output_directory, capture_file)):
                            LPCM_DATA[channel] = capture_file

                    # Log the output
                    send_udp(sock, config['udp']['ip'], config['udp']['port'], LPCM_DATA)
                    lpcm_output.write(
                        "%s %s %s *\n" % (
                            LPCM_DATA['time'],
                            LPCM_DATA['class'],
                            json.dumps(LPCM_DATA),
                        ))
                    lpcm_output.flush()
            except KeyboardInterrupt:
                util.DONE = True
            except Exception as ex:
                print("LPCM Logger Exception: %s" % ex)
                time.sleep(util.ERROR_DELAY)

def lpcm_logger_wrapper(output_directory):
    """ Wrapper Around LPCM Logger Function """
    try:
        lpcm_logger(output_directory)
    except Exception as ex:
        print("LPCM Logger Exception: %s" % ex)
    print("LPCM Done")
    util.DONE = True

# MAIN START

if __name__ == "__main__":
    # Output Directory
    try:
        HOST_NAME = ''
        PORT_NUMBER = int(sys.argv[1])
        OUTPUT = sys.argv[2]
    except IndexError:
        PORT_NUMBER = 8083
        OUTPUT = "/root/gps-data"

    # Web Server
    Twww = threading.Thread(name="W", target=util.web_server, args=(HOST_NAME,PORT_NUMBER, ThreadedHTTPServer, MyHandler))
    Twww.start()

    try:
        lpcm_logger_wrapper(OUTPUT)
    except KeyboardInterrupt:
        util.DONE = True

    Twww.join()
