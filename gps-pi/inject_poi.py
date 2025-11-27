import json
import socket

def send_udp(sock, ip_addr, port, obj):
    sock.sendto(json.dumps(obj).encode(), (ip_addr, port))

with open("config.json") as infile:
    config = json.loads(infile.read())

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

obj = {
    "class": "POI",
    "source": "Test",
    "description": "Test Data Point",
    "metadata": {}
}

send_udp(sock, config['analyzer']['udp']['host'], config['analyzer']['udp']['port'], obj)
