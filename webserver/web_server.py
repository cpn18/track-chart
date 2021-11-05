#!/usr/bin/python3
"""
Web Server
"""

import sys
from urllib.parse import urlparse
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

import util
import pirail_web as application

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    """ Web Handler """

    def do_GET(self):
        """Respond to a GET request."""

        url = urlparse(self.path)
        qsdict = parse_qs(url.query)

        path = url.path

        for match in application.MATCHES:
            groups = match['pattern'].match(self.command + " " + path)
            if groups is not None:
                match['handler'](self, groups, qsdict)
                break
        else:
            self.send_error(404, "File Not Found")

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
