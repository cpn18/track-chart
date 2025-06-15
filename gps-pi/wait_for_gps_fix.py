#!/usr/bin/python3
"""
Wait for GPS Fix and Set System Time
"""
import os
import sys
import threading
import html
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import http.client
import util

# PyLint doesn't like this
config = util.read_config()
TYPE = config['gps']['type']
if TYPE == 'gpsd':
    import gps
elif TYPE == 'witmotion':
    import witmotionjygpsimu as gps
else:
    sys.exit(0)

REPORT = {}

HTML_TEMPLATE = """<html>
  <head>
    <meta http-equiv=\"refresh\" content=\"1;URL='/'\" />
  </head>
  <body>
    <h1 align=center>Waiting for GPS Sync... Check Antenna!</h1>
    <p>%s</p>
  </body>
</html>
"""

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    """ Web Handler """
    def do_GET(self):
        """ GET Handler """
        if self.path == "/favicon.ico":
            self.send_error(http.client.NOT_FOUND)
        else:
            output = (HTML_TEMPLATE % html.escape(str(REPORT))).encode('utf-8')
            self.send_response(http.client.OK)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(output)))
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
    global REPORT

    if TYPE == "gpsd":
        # Listen on port 2947 (gpsd) of localhost
        session = gps.gps(mode=gps.WATCH_ENABLE)
    else:
        session = gps.WitMotionJyGpsImu(config['gps']['serial'], None, None, config)

    try:
        while True:
            report = session.next()
            if TYPE == "gpsd":
                REPORT = str(report)

                if report['class'] != 'TPV':
                    continue
                if hasattr(report, 'mode') and report.mode == 1:
                    continue
                if hasattr(report, 'time'):
                    set_date(report.time)
                    return 0
            else:
                for lines in report:
                    for timestamp, typeclass, obj in lines:
                        REPORT = str(obj)
                        if typeclass != 'TPV':
                            continue
                        if 'mode' in obj and obj['mode'] == 1:
                            continue
                        if 'time' in obj:
                            set_date(obj['time'])
                            session.done()
                            return 0

    except Exception as ex:
        print(ex)

    return 1

def web_server(pirail_httpd):
    """ Web Server Main Thread """
    pirail_httpd.serve_forever()

if __name__ == "__main__":
    httpd = ThreadedHTTPServer(("", 80), MyHandler)
    Twww = threading.Thread(target=web_server, args=(httpd,))
    Twww.start()

    # Make sure we have a time sync
    status = wait_for_timesync()
    httpd.shutdown()
    httpd.server_close()
    Twww.join()

    sys.exit(status)
