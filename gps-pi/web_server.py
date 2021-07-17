#!/usr/bin/python3
"""
GPS / ACCEL LIDAR Logger V9
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
import requests



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
        "imu": {"log": True, "x": "x", "y": "y", "z": "z"},
        "gps": {"log": True},
        "lidar": {"log": True},
        "audio": {"log": True},
    }

CONFIG['class'] = "CONFIG"
CONFIG['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def get_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp") as t:
        return int(t.read())/1000

class MyHandler(BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        global CURRENT
        global DONE
        global RESTART
        global HOLD
        global MEMO

        content_type = "text/html; charset=utf-8"

        if s.path == "/poweroff":
            content_type = "application/json"
            output = "{\"message\": \"Shutting down...\"}"
            DONE = True
            RESTART = False
            os.system("shutdown --poweroff +1")
        elif s.path == "/reset":
            content_type = "application/json"
            output = "{\"message\": \"Resetting...\"}"
            DONE = True
        elif s.path.startswith("/mark?memo="):
            HOLD = 1
            MEMO = s.path.replace("/mark?memo=", "")
            content_type = "application/json"
            output = "{\"message\": \"Marked...\"}"
        elif s.path.startswith("/hold?memo="):
            HOLD = 15 
            MEMO = s.path.replace("/hold?memo=", "")
            content_type = "application/json"
            output = "{\"message\": \"Holding...\"}"
        elif s.path.startswith("/setup?"):
            for var in s.path.split("?")[1].split("&"):
                key, value = var.split("=")
                CONFIG['imu'][key]=value.lower()
            content_type = "application/json"
            output = "{\"message\": \"Stored...\"}"
            with open("config.json", "w") as f:
                CONFIG['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                f.write(json.dumps(CONFIG))
            DONE = True
        elif s.path == "/lidar":
            content_type = "application/json"
            output = json.dumps(LIDAR_DATA)
        elif s.path == "/gps":
            content_type = "application/json"
            response = requests.get("http://localhost:8080/gps")
            if response:
                output = response.json()
                output.update({
                    'temp': get_temperature(),
                })
                output = json.dumps(output)
            else:
                s.send_error(response.status_code, respsonse.reason)
                return
        elif s.path == "/jquery-3.4.1.min.js":
            with open("jquery-3.4.1.min.js", "r") as j:
                output = j.read()
        elif s.path == "/lidar.html":
            with open("lidar.html", "r") as j:
                output = j.read()
        elif s.path == "/gps.html":
            with open("gps.html", "r") as j:
                output = j.read()
        elif s.path == "/setup.html":
            with open("setup.html", "r") as j:
                output = j.read()
        elif s.path == "/favicon.ico":
            output = ""
        else:
            output = "<html><head><title>RPi/GPS/IMU</title></head>"
            output += "<body>"
            output += "<p>You accessed path: %s</p>" % s.path
            output += "</body></html>"

        s.send_response(200)
        s.send_header("Content-type", content_type)
        s.send_header("Content-length", str(len(output)))
        s.end_headers()
        s.wfile.write(output.encode('utf-8'))

def web_server(host_name, port_number):
    global DONE
    
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

def mylog(msg):
    logtime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    if isinstance(msg, str):
        msg = {"log": msg}
    print("%s LOG '%s' *" % (logtime, json.dumps(msg)))

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

if __name__ == "__main__":
    HOST_NAME = ''
    # Command Line Arguments
    try:
        PORT_NUMBER = int(sys.argv[1])
        OUTPUT = sys.argv[2]
    except IndexError:
        PORT_NUMBER = 80
        OUTPUT = "/root/gps-data"

    # Web Server
    web_server(HOST_NAME, PORT_NUMBER)
