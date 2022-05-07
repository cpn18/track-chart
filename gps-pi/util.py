#!/usr/bin/python3
"""
Utilities
"""
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
    with open("config.json", "r") as config_file:
        config = json.loads(config_file.read())

    with open("version.txt", "r") as version_file:
        config['sw_version'] = version_file.readline()

    config['class'] = "CONFIG"
    config['time'] = timestamp()
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
