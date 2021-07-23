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


# Configure Axis
def read_config():
    """ Read Configuration """
    with open("config.json", "r") as config_file:
        config = json.loads(config_file.read())

    config['class'] = "CONFIG"
    config['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return config

def write_config():
    """ Write Configuration """
    with open("config.json", "w") as config_file:
        CONFIG['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        config_file.write(json.dumps(CONFIG))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Threaded HTTP Server """

class MyHandler(BaseHTTPRequestHandler):
    """ Web Handler """
    def do_GET(self):
        """Respond to a GET request."""
        global DONE
        global HOLD
        global MEMO

        content_type = "text/html; charset=utf-8"

        if self.path == "/poweroff":
            content_type = "application/json"
            output = "{\"message\": \"Shutting down...\"}"
            DONE = True
            os.system("shutdown --poweroff +1")
        elif self.path == "/reset":
            content_type = "application/json"
            output = "{\"message\": \"Resetting...\"}"
            DONE = True
        elif self.path.startswith("/mark?memo="):
            HOLD = 1
            MEMO = self.path.replace("/mark?memo=", "")
            content_type = "application/json"
            output = "{\"message\": \"Marked...\"}"
        elif self.path.startswith("/hold?memo="):
            content_type = "application/json"
            headers = {
                "accept": content_type,
            }
            response = requests.get(
                "http://localhost:8080" + self.path;
                headers=headers,
            )
            if response.status_code != 200:
                self.send_error(response.status_code, response.reason)
                return
            output = json.dumps(response.json())
        elif self.path == "/setup.html":
            with open("setup.html", "r") as j:
                output = j.read()
        elif self.path.startswith("/setup?"):
            for var in self.path.split("?")[1].split("&"):
                key, value = var.split("=")
                CONFIG['imu'][key]=value.lower()
            content_type = "application/json"
            output = "{\"message\": \"Stored...\"}"
            write_config()
            DONE = True
        elif self.path == "/" or self.path == "/index.html":
            with open("index.html", "r") as j:
                output = j.read()
        elif self.path == "/gps.html":
            with open("gps.html", "r") as j:
                output = j.read()
        elif self.path == "/gps-stream":
            if CONFIG['gps']['enable'] is False:
                self.send_error(404, "Not Enabled")
                return

            content_type = "text/event-stream"
            headers = {
                "accept": content_type,
            }
            response = requests.get(
                "http://localhost:8080/gps-stream",
                headers=headers,
                stream=True,
            )
            if response.status_code != 200:
                self.send_error(response.status_code, response.reason)
                return

            self.send_response(response.status_code)
            self.send_header("Content-type", response.headers['content-type'])
            self.end_headers()
            while not DONE:
                for line in response.iter_lines():
                    line = (line.decode('utf-8') + "\n").encode('utf-8')
                    self.wfile.write(line)
            return
        elif self.path == "/gps":
            content_type = "application/json"
            response = requests.get("http://localhost:8080/gps")
            if response:
                output = json.dumps(response.json())
            else:
                self.send_error(response.status_code, response.reason)
                return
        elif self.path == "/imu.html":
            with open("imu.html", "r") as j:
                output = j.read()
        elif self.path == "/imu":
            content_type = "application/json"
            response = requests.get("http://localhost:8081/imu")
            if response:
                output = response.json()
                output = json.dumps(output)
            else:
                self.send_error(response.status_code, response.reason)
                return
        elif self.path == "/imu-stream":
            if CONFIG['imu']['enable'] is False:
                self.send_error(404, "Not Enabled")
                return

            content_type = "text/event-stream"
            headers = {
                "accept": content_type,
            }
            response = requests.get(
                "http://localhost:8081/imu-stream",
                headers=headers,
                stream=True,
            )
            if response.status_code != 200:
                self.send_error(response.status_code, response.reason)
                return

            self.send_response(response.status_code)
            self.send_header("Content-type", response.headers['content-type'])
            self.end_headers()
            while not DONE:
                for line in response.iter_lines():
                    line = (line.decode('utf-8') + "\n").encode('utf-8')
                    self.wfile.write(line)
            return
        elif self.path == "/jquery-3.4.1.min.js":
            with open("jquery-3.4.1.min.js", "r") as j:
                output = j.read()
        elif self.path == "/lidar.html":
            with open("lidar.html", "r") as j:
                output = j.read()
        elif self.path == "/lidar":
            content_type = "application/json"
            response = requests.get("http://localhost:8082/lidar")
            if response:
                output = response.json()
                output = json.dumps(output)
            else:
                self.send_error(response.status_code, response.reason)
                return
        elif self.path == "/lidar-stream":
            if CONFIG['lidar']['enable'] is False:
                self.send_error(404, "Not Enabled")
                return

            content_type = "text/event-stream"
            headers = {
                "accept": content_type,
            }
            response = requests.get(
                "http://localhost:8082/lidar-stream",
                headers=headers,
                stream=True,
            )
            if response.status_code != 200:
                self.send_error(response.status_code, response.reason)
                return

            self.send_response(response.status_code)
            self.send_header("Content-type", response.headers['content-type'])
            self.end_headers()
            while not DONE:
                for line in response.iter_lines():
                    line = (line.decode('utf-8') + "\n").encode('utf-8')
                    self.wfile.write(line)
            return
        elif self.path == "/lpcm.html":
            with open("lpcm.html", "r") as j:
                output = j.read()
        elif self.path == "/lpcm":
            content_type = "application/json"
            response = requests.get("http://localhost:8083/lpcm")
            if response:
                output = response.json()
                output = json.dumps(output)
            else:
                self.send_error(response.status_code, response.reason)
                return
        elif self.path == "/lpcm-stream":
            if CONFIG['lpcm']['enable'] is False:
                self.send_error(404, "Not Enabled")
                return

            content_type = "text/event-stream"
            headers = {
                "accept": content_type,
            }
            response = requests.get(
                "http://localhost:8083/lpcm-stream",
                headers=headers,
                stream=True,
            )
            if response.status_code != 200:
                self.send_error(response.status_code, response.reason)
                return

            self.send_response(response.status_code)
            self.send_header("Content-type", response.headers['content-type'])
            self.end_headers()
            while not DONE:
                for line in response.iter_lines():
                    line = (line.decode('utf-8') + "\n").encode('utf-8')
                    self.wfile.write(line)
            return
        elif self.path == "/favicon.ico":
            output = ""
        else:
            self.send_error(404, self.path)
            return

        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.send_header("Content-length", str(len(output)))
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))

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
            print(ex)
    httpd.shutdown()
    httpd.server_close()

if __name__ == "__main__":
    # MAIN START
    DONE = False
    HOLD = -1
    MEMO = ""

    HOST_NAME = ''

    # Command Line Arguments
    try:
        PORT_NUMBER = int(sys.argv[1])
        OUTPUT = sys.argv[2]
    except IndexError:
        PORT_NUMBER = 80
        OUTPUT = "/root/gps-data"

    CONFIG = read_config()

    # Web Server
    web_server(HOST_NAME, PORT_NUMBER)
