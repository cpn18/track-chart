#!/usr/bin/python3
"""
Wait for GPS Fix and Set System Time
"""
import os
import sys
import gps
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import http.client

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_error(http.client.NOT_FOUND)
        else:
            output="<html><head><meta http-equiv=\"refresh\" content=\"1;URL='/'\" /></head><body><h1 align=center>Waiting for GPS Sync... Check Antenna!</h1></body></html>"
            output = output.encode('utf-8')
            self.send_response(http.client.OK)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", str(len(output)))
            self.end_headers()
            self.wfile.write(output)

def set_date(gps_date):
    """ Set the system clock """
    sys_date = "%s%s%s%s%s.%s" % (
        gps_date[5:7],
        gps_date[8:10],
        gps_date[11:13],
        gps_date[14:16],
        gps_date[0:4],
        gps_date[17:19])
    command = "date --utc %s > /dev/null" %  sys_date
    os.system(command)

def wait_for_timesync():
    """ Wait for Time Sync """

    # Listen on port 2947 (gpsd) of localhost
    session = gps.gps(mode=gps.WATCH_ENABLE)

    done = False
    while not done:
        try:
            report = session.next()
            if report['class'] != 'TPV':
                continue
            if hasattr(report, 'mode') and report.mode == 1:
                # can't trust a mode=1 time
                continue
            if hasattr(report, 'time'):
                print(report.time)
                set_date(report.time)
                done = True
        except Exception as ex:
            print(ex)
            sys.exit(1)

def web_server(httpd):
    httpd.serve_forever()

if __name__ == "__main__":
    httpd = ThreadedHTTPServer(("", 80), MyHandler)
    Twww = threading.Thread(target=web_server, args=(httpd,))
    Twww.start()

    # Make sure we have a time sync
    wait_for_timesync()
    httpd.shutdown()
    httpd.server_close()
    Twww.join()
    sys.exit(0)
