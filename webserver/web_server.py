#!/usr/bin/python3
"""
Web Server
"""

import sys
from urllib.parse import urlparse
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from http import HTTPStatus

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

        for match in application.MATCHES:
            groups = match['pattern'].match(self.command + " " + url.path)
            if groups is not None:
                try:
                    match['handler'](self, groups, qsdict)
                except BrokenPipeError as ex:
                    print("ERROR: %s" % ex)
                break
        else:
            self.send_error(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.description)

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
