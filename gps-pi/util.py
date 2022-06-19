#!/usr/bin/python3
"""
Utilities
"""
import os
import json
import datetime

# Event-Stream Interval
STREAM_DELAY = 1 # Seconds

# Data File API Version
DATA_API = 10

# Error Delay
ERROR_DELAY = 5 # Seconds

# Done Flag
DONE = False

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def read_config():
    """ Read Configuration """
    if os.path.isfile("config.json"):
        with open("config.json", "r") as config_file:
            config = json.loads(config_file.read())
    else:
        with open("config.json.sample", "r") as config_file:
            config = json.loads(config_file.read())

    if os.path.isfile("version.txt"):
        with open("version.txt", "r") as version_file:
            config['sw_version'] = version_file.readline().rstrip()
    else:
        config['sw_version'] = "Unknown"

    config['class'] = "CONFIG"
    config['time'] = timestamp()

    if os.path.isfile("/etc/timezone"):
        with open("/etc/timezone") as timezone_file:
            config['timezone'] = timezone_file.readline().rstrip()
    else:
        config['timezone'] = "Unknown"

    return config

def write_config(config):
    """ Write Configuration """
    with open("config.json", "w") as config_file:
        config['time'] = timestamp()
        config_file.write(json.dumps(config, indent=4))

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
