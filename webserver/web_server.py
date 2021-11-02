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
import util

WEBROOT = "webroot"
DATAROOT = "data"

SORTBY = "mileage"

MIME_MAP = {
    ".html": "text/html",
    ".txt": "text/plain",
    ".js": "text/javascript",
    ".json": "application/json",
    "default": "application/octet-stream",
}

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    """ Web Handler """

    def do_GET(self):
        """Respond to a GET request."""

        # Defaults
        content_type = "text/html"
        output = ""

        # Hardcoded rewrite
        if self.path == "/":
            self.path = "index.html"

        if self.path.startswith("/data/"):
            # Data Fetching API
            # GET /data/[filename]
            pathname = os.path.join(DATAROOT, self.path.split("/")[2])
            if not os.path.exists(pathname):
                self.send_error(404, "File Not Found")
                return
            else:
                data = []
                with open(pathname) as j:
                    for line in j:
                        obj = json.loads(line)
                        # Sample method to thin the data set
                        if obj['class'] == "ATT":
                            data.append({
                                'class': obj['class'],
                                'time': obj['time'],
                                'mileage': obj['mileage'],
                                'acc_z': obj['acc_z'],
                            })

                # Sort the data
                if SORTBY is not None:
                    data = sorted(data, key=lambda k: k[SORTBY], reverse=False)

                content_type = MIME_MAP[".json"]
                output = json.dumps(data, indent=4) + "\n"
        else:
            # Generic File Handler API
            # GET /[path]
            pathname = os.path.join(WEBROOT, self.path)
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

        # If we made it this far, then send output to the browser
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.send_header("Content-length", str(len(output)))
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))

if __name__ == "__main__":
    # MAIN START

    # Command Line Arguments
    try:
        HOST_NAME = ''
        PORT_NUMBER = int(sys.argv[1])
    except IndexError:
        PORT_NUMBER = 8080

    # Web Server
    util.web_server(HOST_NAME, PORT_NUMBER, ThreadedHTTPServer, MyHandler)
