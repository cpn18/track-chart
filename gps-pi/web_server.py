#!/usr/bin/python3
"""
Web Server
"""
#pylint: disable=too-many-return-statements
#pylint: disable=too-many-branches
#pylint: disable=too-many-statements
import os
import sys
import time
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import http.client
import requests
import util

DOCUMENT_MAP = {
    "/": "htdocs/index.html",
    "/pirail.css": "css/pirail.css",
    "/index.html": "htdocs/index.html",
    "/setup.html": "htdocs/setup.html",
    "/gps.html": "htdocs/gps.html",
    "/odometer.html": "htdocs/odometer.html",
    "/imu.html": "htdocs/imu.html",
    "/lidar.html": "htdocs/lidar.html",
    "/lpcm.html": "htdocs/lpcm.html",
    "/favicon.ico": "htdocs/favicon.ico",
    "/version.txt": "version.txt",
    "/jquery.js": "js/jquery-3.7.0.min.js",
    "/pirail_setup.js": "js/pirail_setup.js",
    "/pirail_dashboard.js": "js/pirail_dashboard.js",
    "/pirail_gps.js": "js/pirail_gps.js",
    "/pirail_odometer.js": "js/pirail_odometer.js",
    "/pirail_imu.js": "js/pirail_imu.js",
    "/pirail_lidar.js": "js/pirail_lidar.js",
    "/pirail_lpcm.js": "js/pirail_lpcm.js",
    "/pirail_draw.js": "js/pirail_draw.js",
}

MIME_MAP = {
    ".html": "text/html",
    ".txt": "text/plain",
    ".js": "text/javascript",
    ".css": "text/css",
    ".json": "application/json",
    "default": "application/octet-stream",
}

SHUTDOWN_DELAY="now"

def get_sys_data():
    """ Get System Data """
    stat = os.statvfs(OUTPUT)

    sys_data = {
        "used_percent": 100 - int(100 * stat.f_bavail / stat.f_blocks),
        "sw_version": CONFIG['sw_version'],
    }
    return sys_data

def check_enabled(configs):
    """ Determine if enabled """
    for config in configs:
        if config['enable'] or config['host'] not in ['localhost', '127.0.0.1']:
            return (config['host'], config['port'])
    return False

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    """ Web Handler """

    def mini_proxy(self, url, verbose=False):
        """ Mini Web Proxy """

        # Try to establish the connection
        stream = self.headers['Accept'] == 'text/event-stream'
        try:
            response = requests.get(
                url,
                headers=self.headers,
                stream=stream,
            )
        except requests.exceptions.ConnectionError as ex:
            self.send_error(http.client.SERVICE_UNAVAILABLE, str(ex))
            return

        # Error response
        if response.status_code != http.client.OK:
            self.send_error(response.status_code, response.reason)
            return

        if verbose:
            print("url: %s, proxying: headers=%s" % (url, response.headers))

        # Start the response
        self.send_response(http.client.OK)

        # Copy certain response headers
        for header in ['Content-Type']:
            self.send_header(header, response.headers[header])

        # If not streaming, must send the content-length
        if not stream:
            output = response.content
            if not isinstance(output, bytes):
                output = output.encode('utf-8')
            self.send_header("Content-Length", str(len(output)))

        # End of HTTP Headers
        self.end_headers()

        if not stream:
            # Not streaming, just send the data
            self.wfile.write(output)
        else:
            # Streaming, send each line
            try:
                for output in response.iter_content():
                    self.wfile.write(output)
            except (BrokenPipeError, ConnectionResetError) as ex:
                if verbose:
                    print("url: %s, exception=%s" % (url, ex))

        if verbose:
            print("url: %s, exiting" % url)

    def do_POST(self):
        """ POST Handler """
        if self.path.startswith("/setup"):
            data = json.loads(self.rfile.read(int(self.headers['content-length'])))
            for field in ['gps', 'imu', 'lidar', 'hpslidar', 'lpcm']:
                CONFIG[field].update(data[field])
            util.DONE = True
            util.write_config(CONFIG)
            content_type = "application/json"
            output = json.dumps({
                "message": "Stored. Rebooting...",
            })
            os.system("shutdown --reboot %s" % SHUTDOWN_DELAY)
        else:
            self.send_error(http.client.NOT_FOUND, self.path)
            return

        # If we made it this far, then send output to the browser
        output = output.encode('utf-8')
        self.send_response(http.client.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(output)))
        self.end_headers()
        self.wfile.write(output)

    def do_GET(self):
        """Respond to a GET request."""

        content_type = "text/html"

        if self.path in DOCUMENT_MAP:
            pathname = DOCUMENT_MAP[self.path]
            _, extension = os.path.splitext(pathname)
            if not os.path.exists(pathname):
                self.send_error(http.client.NOT_FOUND, "File Not Found")
                return

            if not extension in MIME_MAP:
                extension = 'default'
            content_type = MIME_MAP[extension]
            with open(pathname, 'rb') as j:
                output = j.read()

        elif self.path == "/setup":
            content_type = "application/json"
            output = json.dumps(CONFIG)

        elif self.path == "/poweroff":
            util.DONE = True
            content_type = "application/json"
            output = json.dumps({
                "message": "Shutting down...",
            })
            os.system("shutdown --poweroff %s" % SHUTDOWN_DELAY)

        elif self.path == "/reset":
            util.DONE = True
            content_type = "application/json"
            output = json.dumps({
                "message": "Rebooting...",
            })
            os.system("shutdown --reboot %s" % SHUTDOWN_DELAY)

        elif self.path.startswith("/gps/"):
            enabled = check_enabled([CONFIG['gps'], CONFIG['gpsimu']])
            if enabled is False:
                self.send_error(http.client.SERVICE_UNAVAILABLE, "Not Enabled")
            else:
                self.mini_proxy(
                    "http://%s:%d%s" % (enabled[0], enabled[1], self.path),
                )
            return

        elif self.path.startswith("/imu/"):
            enabled = check_enabled([CONFIG['imu'], CONFIG['gpsimu']])
            if enabled is False:
                self.send_error(http.client.SERVICE_UNAVAILABLE, "Not Enabled")
            else:
                self.mini_proxy(
                    "http://%s:%d%s" % (enabled[0], enabled[1], self.path),
                )
            return

        elif self.path.startswith("/lidar/"):
            enabled = check_enabled([CONFIG['lidar'], CONFIG['hpslidar']])
            if enabled is False:
                self.send_error(http.client.SERVICE_UNAVAILABLE, "Not Enabled")
            else:
                self.mini_proxy(
                    "http://%s:%d%s" % (enabled[0], enabled[1], self.path),
                )
            return

        elif self.path.startswith("/lpcm/"):
            enabled = check_enabled([CONFIG['lpcm']])
            if enabled is False:
                self.send_error(http.client.SERVICE_UNAVAILABLE, "Not Enabled")
            else:
                self.mini_proxy(
                    "http://%s:%d%s" % (enabled[0], enabled[1], self.path),
                )
            return

        elif self.path.startswith("/sys/"):
            stream = self.headers['Accept'] == 'text/event-stream'

            # Start the response
            self.send_response(http.client.OK)

            # If not streaming, must send the content-length
            if not stream:
                content_type = "application/json"
                output = json.dumps(get_sys_data())
                self.send_header("Content-Length", str(len(output)))
            else:
                content_type = "text/event-stream"

            # Send the content-type
            self.send_header("Content-Type", content_type)

            # End of HTTP Headers
            self.end_headers()

            if not stream:
                # Not streaming, just send the data
                self.wfile.write(output)
            else:
                # Streaming, generate new data each time
                try:
                    while not util.DONE:
                        output = "event: sys\ndata: " + json.dumps(get_sys_data()) + "\n\n"
                        self.wfile.write(output.encode('utf-8'))
                        self.wfile.flush()
                        time.sleep(util.STREAM_DELAY)
                except (BrokenPipeError, ConnectionResetError):
                    pass
            return

        else:
            self.send_error(http.client.NOT_FOUND, self.path)
            return

        # If we made it this far, then send output to the browser
        if not isinstance(output, bytes):
            output = output.encode('utf-8')
        self.send_response(http.client.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(output)))
        self.end_headers()
        self.wfile.write(output)

if __name__ == "__main__":
    # MAIN START

    # Command Line Arguments
    try:
        HOST_NAME = ''
        PORT_NUMBER = int(sys.argv[1])
        OUTPUT = sys.argv[2]
    except IndexError:
        PORT_NUMBER = 80
        OUTPUT = "/root/gps-data"

    CONFIG = util.read_config()

    # Web Server
    util.web_server(HOST_NAME, PORT_NUMBER, ThreadedHTTPServer, MyHandler)
