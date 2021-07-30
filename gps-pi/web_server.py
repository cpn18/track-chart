#!/usr/bin/python3
"""
Web Server
"""

import os
import sys
import time
import datetime
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import requests

DOCUMENT_MAP = {
    "/": "htdocs/index.html",
    "/index.html": "htdocs/index.html",
    "/setup.html": "htdocs/setup.html",
    "/gps.html": "htdocs/gps.html",
    "/imu.html": "htdocs/imu.html",
    "/lidar.html": "htdocs/lidar.html",
    "/lpcm.html": "htdocs/lpcm.html",
    "/favicon.ico": "htdocs/favicon.ico",
    "/version.txt": "version.txt",
    "/jquery.js": "js/jquery-3.6.0.min.js",
    "/pirail_setup.js": "js/pirail_setup.js",
    "/pirail_dashboard.js": "js/pirail_dashboard.js",
    "/pirail_gps.js": "js/pirail_gps.js",
    "/pirail_imu.js": "js/pirail_imu.js",
    "/pirail_lidar.js": "js/pirail_lidar.js",
    "/pirail_lpcm.js": "js/pirail_lpcm.js",
    "/pirail_draw.js": "js/pirail_draw.js",
}

MIME_MAP = {
    ".html": "text/html",
    ".txt": "text/plain",
    ".js": "text/javascript",
    ".json": "application/json",
    "default": "application/octet-stream",
}

# Configure Axis
def read_config():
    """ Read Configuration """
    with open("config.json", "r") as config_file:
        config = json.loads(config_file.read())

    config['class'] = "CONFIG"
    config['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return config

def write_config():
    """ Write Configuration """
    with open("config.json", "w") as config_file:
        CONFIG['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        config_file.write(json.dumps(CONFIG, indent=4))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    """ Web Handler """
    def do_POST(self):
        global DONE
        if self.path.startswith("/setup"):
            data = json.loads(self.rfile.read(int(self.headers['content-length'])))
            for field in ['gps', 'imu', 'lidar', 'lpcm']:
                CONFIG[field].update(data[field])
            DONE = True
            write_config()
            content_type = "application/json"
            output = json.dumps({
                "message": "Stored. Rebooting...",
            })
            os.system("shutdown --reboot +1")
        else:
            self.send_error(404, self.path)
            return

        # If we made it this far, then send output to the browser
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.send_header("Content-length", str(len(output)))
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))

    def do_GET(self):
        """Respond to a GET request."""
        global DONE

        content_type = "text/html"

        if self.path in DOCUMENT_MAP:
            pathname = DOCUMENT_MAP[self.path]
            _, extension = os.path.splitext(pathname)
            if not os.path.exists(pathname):
                self.send_error(404, "File Not Found")
                return
            else:
                if not extension in MIME_MAP:
                    extension = 'default'
                content_type = MIME_MAP[extension]
                with open(pathname) as j:
                    output = j.read()
        elif self.path == "/setup":
            content_type = "application/json"
            output = json.dumps(CONFIG)
        elif self.path == "/poweroff":
            DONE = True
            content_type = "application/json"
            output = json.dumps({
                "message": "Shutting down...",
            })
            os.system("shutdown --poweroff +1")
        elif self.path == "/reset":
            DONE = True
            content_type = "application/json"
            output = json.dumps({
                "message": "Rebooting...",
            })
            os.system("shutdown --reboot +1")
        elif self.path == "/gps":
            content_type = "application/json"
            response = requests.get("http://localhost:%d/gps" % CONFIG['gps']['port'])
            if response:
                output = json.dumps(response.json())
            else:
                self.send_error(response.status_code, response.reason)
                return
        elif self.path == "/gps-stream":
            if CONFIG['gps']['enable'] is False:
                self.send_error(404, "Not Enabled")
                return

            content_type = "text/event-stream"
            headers = {
                "accept": content_type,
            }
            response = requests.get(
                "http://localhost:%d/gps-stream" % CONFIG['gps']['port'],
                headers=headers,
                stream=True,
            )
            if response.status_code != 200:
                self.send_error(response.status_code, response.reason)
                return

            self.send_response(response.status_code)
            self.send_header("Content-type", response.headers['content-type'])
            self.end_headers()
            while not DONE:
                try:
                    for line in response.iter_lines():
                        line = (line.decode('utf-8') + "\n").encode('utf-8')
                        self.wfile.write(line)
                except BrokenPipeError:
                    break
            return
        elif self.path.startswith("/mark?memo=") or self.path.startswith("/hold?memo="):
            content_type = "application/json"
            headers = {
                "accept": content_type,
            }
            response = requests.get(
                "http://localhost:%d" % CONFIG['gps']['port'] + self.path,
                headers=headers,
            )
            if response.status_code != 200:
                self.send_error(response.status_code, response.reason)
                return
            output = json.dumps(response.json())
        elif self.path == "/imu":
            content_type = "application/json"
            response = requests.get("http://localhost:%d/imu" % CONFIG['imu']['port'])
            if response:
                output = response.json()
                output = json.dumps(output)
            else:
                self.send_error(response.status_code, response.reason)
                return
        elif self.path == "/imu-stream":
            if CONFIG['imu']['enable'] is False:
                self.send_error(404, "Not Enabled")
                return

            content_type = "text/event-stream"
            headers = {
                "accept": content_type,
            }
            response = requests.get(
                "http://localhost:%d/imu-stream" % CONFIG['imu']['port'],
                headers=headers,
                stream=True,
            )
            if response.status_code != 200:
                self.send_error(response.status_code, response.reason)
                return

            self.send_response(response.status_code)
            self.send_header("Content-type", response.headers['content-type'])
            self.end_headers()
            while not DONE:
                try:
                    for line in response.iter_lines():
                        line = (line.decode('utf-8') + "\n").encode('utf-8')
                        self.wfile.write(line)
                except BrokenPipeError:
                    break
            return
        elif self.path == "/lidar":
            content_type = "application/json"
            response = requests.get("http://localhost:%d/lidar" % CONFIG['lidar']['port'])
            if response:
                output = response.json()
                output = json.dumps(output)
            else:
                self.send_error(response.status_code, response.reason)
                return
        elif self.path == "/lidar-stream":
            if CONFIG['lidar']['enable'] is False:
                self.send_error(404, "Not Enabled")
                return

            content_type = "text/event-stream"
            headers = {
                "accept": content_type,
            }
            response = requests.get(
                "http://localhost:%d/lidar-stream" % CONFIG['lidar']['port'],
                headers=headers,
                stream=True,
            )
            if response.status_code != 200:
                self.send_error(response.status_code, response.reason)
                return

            self.send_response(response.status_code)
            self.send_header("Content-type", response.headers['content-type'])
            self.end_headers()
            while not DONE:
                try:
                    for line in response.iter_lines():
                        line = (line.decode('utf-8') + "\n").encode('utf-8')
                        self.wfile.write(line)
                except BrokenPipeError:
                    break
            return
        elif self.path == "/lpcm":
            content_type = "application/json"
            response = requests.get("http://localhost:%d/lpcm" % CONFIG['lpcm']['port'])
            if response:
                output = response.json()
                output = json.dumps(output)
            else:
                self.send_error(response.status_code, response.reason)
                return
        elif self.path == "/lpcm-stream":
            if CONFIG['lpcm']['enable'] is False:
                self.send_error(404, "Not Enabled")
                return

            content_type = "text/event-stream"
            headers = {
                "accept": content_type,
            }
            response = requests.get(
                "http://localhost:%d/lpcm-stream" % CONFIG['lpcm']['port'],
                headers=headers,
                stream=True,
            )
            if response.status_code != 200:
                self.send_error(response.status_code, response.reason)
                return

            self.send_response(response.status_code)
            self.send_header("Content-type", response.headers['content-type'])
            self.end_headers()
            while not DONE:
                try:
                    for line in response.iter_lines():
                        line = (line.decode('utf-8') + "\n").encode('utf-8')
                        self.wfile.write(line)
                except BrokenPipeError:
                    break
            return
        else:
            self.send_error(404, self.path)
            return

        # If we made it this far, then send output to the browser
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.send_header("Content-length", str(len(output)))
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))

def web_server(host_name, port_number):
    """ Web Server """
    global DONE

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

if __name__ == "__main__":
    # MAIN START
    DONE = False

    # Command Line Arguments
    try:
        HOST_NAME = ''
        PORT_NUMBER = int(sys.argv[1])
        OUTPUT = sys.argv[2]
    except IndexError:
        PORT_NUMBER = 80
        OUTPUT = "/root/gps-data"

    CONFIG = read_config()

    # Web Server
    web_server(HOST_NAME, PORT_NUMBER)
