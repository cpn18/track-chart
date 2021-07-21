#!/usr/bin/python3
"""
LPCM Logger V9
"""

import os
import sys
import threading
import time
import datetime
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

ERROR_DELAY = 5
STREAM_DELAY = 1

def read_config():
    """ Read Configuration """
    try:
        with open("config.json", "r") as config_file:
            config = json.loads(config_file.read())
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
                lines = [
                    "event: lpcm\n",
                    "data: " + json.dumps(LPCM_DATA) + "\n",
                    "\n",
                ]
                for line in lines:
                    self.wfile.write(line.encode('utf-8'))
                time.sleep(STREAM_DELAY)
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

def web_server(host_name, port_number):
    """ Web Server """
    global DONE
    # Web Server
    httpd = HTTPServer((host_name, port_number), MyHandler)
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

def audio_logger(output_directory):
    """ Audio Capture Wrapper """
    global DONE, LPCM_DATA

    # Configure
    config = read_config()

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    with open(os.path.join(output_directory,timestamp+"_audio.csv"), "w") as audio_output:
        audio_output.write("#v%d\n" % VERSION)
        audio_output.write("%s %s %s *\n" % (config['time'], config['class'], json.dumps(config)))
        while not DONE:
            try:
                timestamp = datetime.datetime.now()
                filename = timestamp.strftime("%Y%m%d%H%M")
                if os.system("./audio_collect.sh %s %s" % (output_directory, filename)) != 0:
                    time.sleep(ERROR_DELAY)
                else:
                    LPCM_DATA = {
                        "class": "AUDIO",
                        "time": timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    }
                    for channel in ["left", "right"]:
                        capture_file = filename+"_"+channel+".wav"
                        if os.path.isfile(os.path.join(output_directory, capture_file)):
                            LPCM_DATA[channel] = capture_file
                    audio_output.write(
                        "%s %s %s *\n" % (
                            LPCM_DATA['time'],
                            LPCM_DATA['class'],
                            json.dumps(LPCM_DATA),
                        ))
            except KeyboardInterrupt:
                DONE = True
            except Exception as ex:
                print("Audio Logger Exception: %s" % ex)
                time.sleep(ERROR_DELAY)

def audio_logger_wrapper(output_directory):
    """ Wrapper Around Audio Logger Function """
    global DONE
    try:
        audio_logger(output_directory)
    except Exception as ex:
        print("Audio Logger Exception: %s" % ex)
    print("Audio Done")
    DONE = True

# MAIN START
DONE = False
VERSION = 9
LPCM_DATA = {}

# Output Directory
try:
    HOST_NAME = ''
    PORT_NUMBER = int(sys.argv[1])
    OUTPUT = sys.argv[2]
except IndexError:
    PORT_NUMBER = 8083
    OUTPUT = "/root/gps-data"


Twww = threading.Thread(name="W", target=web_server, args=(HOST_NAME,PORT_NUMBER))
Twww.start()

audio_logger_wrapper(OUTPUT)

Twww.join()
