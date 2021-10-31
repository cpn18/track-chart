#!/usr/bin/python3
"""
Utilities
"""

# Event-Stream Interval
STREAM_DELAY = 1 # Seconds

# Data File API Version
DATA_API = 9

# Error Delay
ERROR_DELAY = 5 # Seconds

# Configure Axis
def read_config():
    """ Read Configuration """
    if os.path.isfile("config.json"):
        with open("config.json", "r") as config_file:
            config = json.loads(config_file.read())
    else:
        with open("config.json.sample", "r") as config_file:
            config = json.loads(config_file.read())

    with open("version.txt", "r") as version_file:
        config['sw_version'] = version_file.read()

    config['class'] = "CONFIG"
    config['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return config

def write_config():
    """ Write Configuration """
    with open("config.json", "w") as config_file:
        CONFIG['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        config_file.write(json.dumps(CONFIG, indent=4))

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
            print("WARNING: %s" % ex)
    httpd.shutdown()
    httpd.server_close()
