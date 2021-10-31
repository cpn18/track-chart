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
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

import util

DONE = False
LPCM_DATA = {}

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    """ Web Request Handler """
    def do_GET(self):
        """Respond to a GET request."""
        global DONE

        content_type = "text/html; charset=utf-8"

        if self.path == "/lpcm":
            content_type = "application/json"
            output = json.dumps(LPCM_DATA)
        elif self.path == "/lpcm-stream":
            content_type = "text/event-stream"
            self.send_response(200)
            self.send_header("content-type", content_type)
            self.end_headers()
            while not DONE:
                try:
                    lines = [
                        "event: lpcm\n",
                        "data: " + json.dumps(LPCM_DATA) + "\n",
                        "\n",
                    ]
                    for line in lines:
                        self.wfile.write(line.encode('utf-8'))
                    time.sleep(util.STREAM_DELAY)
                except (BrokenPipeError, ConnectionResetError):
                    break
            return
        elif self.path == "/lpcm.html":
            with open("lpcm.html", "r") as j:
                output = j.read()
        else:
            self.send_error(404, self.path)
            return

        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.send_header("Content-length", str(len(output)))
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))

def lpcm_logger(output_directory):
    """ LPCM Capture Wrapper """
    global DONE, LPCM_DATA

    # Configure
    config = util.read_config()

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    with open(os.path.join(output_directory,timestamp+"_lpcm.csv"), "w") as lpcm_output:
        lpcm_output.write("#v%d\n" % util.DATA_API)
        lpcm_output.write("%s %s %s *\n" % (config['time'], config['class'], json.dumps(config)))
        while not DONE:
            try:
                timestamp = datetime.datetime.now()
                filename = timestamp.strftime("%Y%m%d%H%M")
                LPCM_DATA = {
                    "class": "LPCM",
                    "time": timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
                for channel in ["left", "right"]:
                    capture_file = filename+"_"+channel+".wav"
                    if os.path.isfile(os.path.join(output_directory, capture_file)):
                        LPCM_DATA[channel] = capture_file

                if os.system("./lpcm_collect.sh %s %s \"%s\"" % (output_directory, filename, config['lpcm']['arecord'])) != 0:
                    time.sleep(util.ERROR_DELAY)
                else:
                    lpcm_output.write(
                        "%s %s %s *\n" % (
                            LPCM_DATA['time'],
                            LPCM_DATA['class'],
                            json.dumps(LPCM_DATA),
                        ))
            except KeyboardInterrupt:
                DONE = True
            except Exception as ex:
                print("LPCM Logger Exception: %s" % ex)
                time.sleep(util.ERROR_DELAY)

def lpcm_logger_wrapper(output_directory):
    """ Wrapper Around LPCM Logger Function """
    global DONE
    try:
        lpcm_logger(output_directory)
    except Exception as ex:
        print("LPCM Logger Exception: %s" % ex)
    print("LPCM Done")
    DONE = True

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
    Twww = threading.Thread(name="W", target=util.web_server, args=(HOST_NAME,PORT_NUMBER))
    Twww.start()

    try:
        lpcm_logger_wrapper(OUTPUT)
    except KeyboardInterrupt:
        DONE = True

    Twww.join()
