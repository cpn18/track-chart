#!/usr/bin/python3
"""
Web Server
"""
import os
import sys
import time
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
import http.client
import requests
import util
import socket
import threading
import datetime

PACKETS = {}
SHUTDOWN_DELAY = "now"

REACT_BUILD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ReactApp/dist")

def parse_time(timestr):
    """Parse the ISO8601 time format: '2024-06-01T11:28:11.000000Z'."""
    timestr = timestr.replace('Z', '')
    return datetime.datetime.fromisoformat(timestr)

def simulate_packets(file_path):
    """Simulate reading JSON data line by line and streaming packets in real time."""
    with open(file_path, 'r') as f:
        lines = f.read().splitlines()  # read file into a list of lines

    if not lines:
        return

    while True:
        # Parse the first line to determine the initial_time
        first_packet = json.loads(lines[0])
        initial_time = parse_time(first_packet['time'])
        simulation_start = time.time()

        # Now iterate through every line/packet
        for line in lines:
            packet = json.loads(line)
            packet_time = parse_time(packet['time'])
            offset = (packet_time - initial_time).total_seconds()
            now_offset = time.time() - simulation_start
            sleep_time = offset - now_offset

            if sleep_time > 0:
                time.sleep(sleep_time)

            PACKETS[packet['class']] = packet



def udp_receiver(ip, port):
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((ip, port))

    while True:
        data, addr = sock.recvfrom(65535) # UDP buffer size
        payload = json.loads(data.decode())
        PACKETS[payload['class']] = payload

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP Server."""

class MyHandler(BaseHTTPRequestHandler):
    """Main HTTP Handler, serves React build plus SSE and special endpoints."""

    def mini_proxy(self, url, verbose=False):
        """ Mini Web Proxy """

        # Try to establish the connection
        stream = self.headers['Accept'] == 'text/event-stream'
        try:
            response = requests.get(
                url,
                headers=self.headers,
                stream=stream,
            )
        except requests.exceptions.ConnectionError as ex:
            self.send_error(http.client.SERVICE_UNAVAILABLE, str(ex))
            return

        # Error response
        if response.status_code != http.client.OK:
            self.send_error(response.status_code, response.reason)
            return

        if verbose:
            print("url: %s, proxying: headers=%s" % (url, response.headers))

        # Start the response
        self.send_response(http.client.OK)

        # Copy certain response headers
        for header in ['Content-Type']:
            self.send_header(header, response.headers[header])

        # If not streaming, must send the content-length
        if not stream:
            output = response.content
            if not isinstance(output, bytes):
                output = output.encode('utf-8')
            self.send_header("Content-Length", str(len(output)))

        # End of HTTP Headers
        self.end_headers()

        if not stream:
            # Not streaming, just send the data
            self.wfile.write(output)
        else:
            # Streaming, send each line
            try:
                for output in response.iter_content():
                    self.wfile.write(output)
            except (BrokenPipeError, ConnectionResetError) as ex:
                if verbose:
                    print("url: %s, exception=%s" % (url, ex))

        if verbose:
            print("url: %s, exiting" % url)

    def send_file(self, filepath, content_type="text/html"):

        """Helper to serve file from disk."""
        if not os.path.exists(filepath):
            self.send_error(http.client.NOT_FOUND, "File Not Found")
            return
        with open(filepath, 'rb') as f:
            data = f.read()
        self.send_response(http.client.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        """Handle POST requests (e.g. /setup)."""
        if self.path.startswith("/setup"):
            data = json.loads(self.rfile.read(int(self.headers['content-length'])))
            # Example: store or update config in util
            for field in ['gps','imu','lidar','hpslidar','lpcm','simulator']:
                if field in data:
                    CONFIG[field].update(data[field])
            util.DONE = True
            util.write_config(CONFIG)
            output_dict = {"message": "Stored. Rebooting..."}
            os.system(f"shutdown --reboot {SHUTDOWN_DELAY}")
            output = json.dumps(output_dict).encode('utf-8')
            self.send_response(http.client.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(output)))
            self.end_headers()
            self.wfile.write(output)
        else:
            self.send_error(http.client.NOT_FOUND, self.path)

    def do_GET(self):
        """Handle GET requests: serve /packets SSE, or fallback to React build."""
        url = urlparse(self.path)
        path = url.path

        if path.startswith("/packets"):
            qsdict = parse_qs(url.query)
            accept_type = self.headers.get('Accept', '')

            # Start building SSE or JSON response
            self.send_response(http.client.OK)
            if accept_type == "text/event-stream":
                # SSE mode
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()

                # Possibly read query params for 'class', 'delay', 'count' etc.
                # e.g. &class=TPV&class=SKY
                param_class = qsdict.get('class', [])
                param_delay = float(qsdict.get('delay', [1])[0])
                param_count = int(qsdict.get('count', [1])[0])

                # If user specified classes, filter. Otherwise, all PACKETS.
                if param_class:
                    filtered = {cls: PACKETS[cls] for cls in param_class if cls in PACKETS}
                else:
                    filtered = PACKETS

                for _ in range(param_count):
                    # Example: if 'TPV' or 'SKY' in filtered, send them
                    if 'TPV' in filtered:
                        msg = f"event: pirail_TPV\ndata: {json.dumps(filtered['TPV'])}\n\n"
                        self.wfile.write(msg.encode('utf-8'))
                    if 'SKY' in filtered:
                        msg = f"event: pirail_SKY\ndata: {json.dumps(filtered['SKY'])}\n\n"
                        self.wfile.write(msg.encode('utf-8'))
                    if 'ATT' in filtered:
                        msg = f"event: pirail_ATT\ndata: {json.dumps(filtered['ATT'])}\n\n"
                        self.wfile.write(msg.encode('utf-8'))
                    if 'LIDAR' in filtered:
                        msg = f"event: pirail_LIDAR\ndata: {json.dumps(filtered['LIDAR'])}\n\n"
                        self.wfile.write(msg.encode('utf-8'))
                    if 'LIDAR3D' in filtered:
                        msg = f"event: pirail_LIDAR\ndata: {json.dumps(filtered['LIDAR3D'])}\n\n"
                        self.wfile.write(msg.encode('utf-8'))
                        self.wfile.flush()
                    time.sleep(param_delay)

            else:
                # Return all packets in JSON
                self.send_header("Content-Type", "application/json")
                output = json.dumps(PACKETS).encode('utf-8')
                self.send_header("Content-Length", str(len(output)))
                self.end_headers()
                self.wfile.write(output)
            return

        elif path == "/IMUzero":
            # TODO: set global zero variable to current pitch and roll
            # Now, when passing ATT packets, they will be compared to the zero val
            return

        elif path == "/config":
            config_json = json.dumps(CONFIG).encode('utf-8')
            self.send_response(http.client.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(config_json)))
            self.end_headers()
            self.wfile.write(config_json)
            return

        # Custom endpoints
        elif path == "/poweroff":
            util.DONE = True
            output = json.dumps({"message": "Shutting down..."}).encode('utf-8')
            os.system(f"shutdown --poweroff {SHUTDOWN_DELAY}")
            self.send_response(http.client.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(output)))
            self.end_headers()
            self.wfile.write(output)
            return

        elif path == "/reset":
            util.DONE = True
            output = json.dumps({"message": "Rebooting..."}).encode('utf-8')
            os.system(f"shutdown --reboot {SHUTDOWN_DELAY}")
            self.send_response(http.client.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(output)))
            self.end_headers()
            self.wfile.write(output)
            return

        elif self.path.startswith("/gps/"):
            enabled = check_enabled([CONFIG['gps'], CONFIG['gpsimu']])
            if enabled is False:
                self.send_error(http.client.SERVICE_UNAVAILABLE, "Not Enabled")
            else:
                self.mini_proxy(
                    "http://%s:%d%s" % (enabled[0], enabled[1], self.path),
                )
            return

        elif self.path.startswith("/imu/"):
            enabled = check_enabled([CONFIG['imu'], CONFIG['gpsimu']])
            if enabled is False:
                self.send_error(http.client.SERVICE_UNAVAILABLE, "Not Enabled")
            else:
                self.mini_proxy(
                    "http://%s:%d%s" % (enabled[0], enabled[1], self.path),
                )
            return

        elif self.path.startswith("/lidar/"):
            enabled = check_enabled([CONFIG['lidar'], CONFIG['hpslidar']])
            if enabled is False:
                self.send_error(http.client.SERVICE_UNAVAILABLE, "Not Enabled")
            else:
                self.mini_proxy(
                    "http://%s:%d%s" % (enabled[0], enabled[1], self.path),
                )
            return

        elif self.path.startswith("/lpcm/"):
            enabled = check_enabled([CONFIG['lpcm']])
            if enabled is False:
                self.send_error(http.client.SERVICE_UNAVAILABLE, "Not Enabled")
            else:
                self.mini_proxy(
                    "http://%s:%d%s" % (enabled[0], enabled[1], self.path),
                )
            return
        elif path.startswith("/sys/"):
            stream = (self.headers.get('Accept') == 'text/event-stream')
            self.send_response(http.client.OK)
            if not stream:
                self.send_header("Content-Type", "application/json")
                data = json.dumps(get_sys_data()).encode('utf-8')
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                try:
                    while not util.DONE:
                        # Your logic to stream system data
                        data = "event: sys\ndata: " + json.dumps(get_sys_data()) + "\n\n"
                        self.wfile.write(data.encode('utf-8'))
                        self.wfile.flush()
                        time.sleep(util.STREAM_DELAY)
                except (BrokenPipeError, ConnectionResetError):
                    pass
            return

        # No endpoints match, serve index.html, let client side routing take care of the rest
        else:
            filepath = os.path.join(REACT_BUILD_DIR, path.lstrip('/'))
            if os.path.isfile(filepath):
                _, ext = os.path.splitext(filepath)
                if ext == '.css':
                    mime = 'text/css'
                elif ext == '.js':
                    mime = 'text/javascript'
                elif ext == '.ico':
                    mime = 'image/x-icon'
                elif ext in ['.png','.jpg','.jpeg','.gif','.svg']:
                    mime = f'image/{ext.replace(".","")}'
                else:
                    mime = 'text/html'
                self.send_file(filepath, content_type=mime)
            else:
                index_path = os.path.join(REACT_BUILD_DIR, "index.html")
                self.send_file(index_path, content_type="text/html")

def get_sys_data():
    """ Get System Data """
    stat = os.statvfs(OUTPUT)

    firmware_name = "/sys/firmware/devicetree/base/model"
    if os.path.exists(firmware_name):
        with open(firmware_name) as infile:
            hwname = infile.read()
    else:
        hwname = "unknown"

    sys_data = {
        "output": OUTPUT,
        "used_percent": 100 - int(100 * stat.f_bavail / stat.f_blocks),
        "sw_version": CONFIG.get('sw_version', 'unknown'),
        "hwname": hwname,
    }
    return sys_data

def check_enabled(configs):
    """Check if any of these config items are enabled."""
    for config in configs:
        if config['enable'] or config['host'] not in ['localhost','127.0.0.1']:
            return (config['host'], config['port'])
    return False

if __name__ == "__main__":
    # MAIN
    try:
        HOST_NAME = ''
        PORT_NUMBER = int(sys.argv[1])
        OUTPUT = sys.argv[2]
    except IndexError:
        PORT_NUMBER = 80
        OUTPUT = "/root/gps-data"

    # read your config
    CONFIG = util.read_config()

    # start either simulator or real UDP listener
    simulator_enabled = CONFIG.get('simulator', {}).get('enable', False)
    if simulator_enabled:
        Tsim = threading.Thread(target=simulate_packets, args=("Data_Wolfeboro.json",), daemon=True)
        Tsim.start()
    else:
        ip = CONFIG['udp']['ip']
        port = CONFIG['udp']['port']
        Tudp = threading.Thread(target=udp_receiver, args=(ip,port), daemon=True)
        Tudp.start()

    # Launch HTTP server
    server = ThreadedHTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)
    print(f"Serving on port {PORT_NUMBER}, build dir={REACT_BUILD_DIR}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    print("Server stopped.")
