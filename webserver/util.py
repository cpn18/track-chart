#!/usr/bin/python3
"""
Utilities
"""
import json
import datetime

# Done Flag
DONE = False

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def web_server(host_name, port_number, server, handler):
    """ Web Server """
    global DONE

    httpd = server((host_name, port_number), handler)
    while not DONE:
        try:
            print("%s Server Starts - %s:%s" % (timestamp(), host_name, port_number))
            httpd.serve_forever()
            print("%s Server Stops - %s:%s" % (timestamp(), host_name, port_number))
        except KeyboardInterrupt:
            DONE = True
        except Exception as ex:
            print("WARNING: %s" % ex)
    httpd.shutdown()
    httpd.server_close()
