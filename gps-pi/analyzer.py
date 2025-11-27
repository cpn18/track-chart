#!/usr/bin/python3
"""
Sample In-Line PiRail Packet Analyzer
"""

import socket
import json

import util


def send_udp(sock, ip_addr, port, obj):
    """ Send Packet """
    sock.sendto(json.dumps(obj).encode(), (ip_addr, port))

def udp_receiver(src_ip, src_port, dest_ip, dest_port):
    """ UDP Packet Receiver """

    # Create the socket
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((src_ip, src_port))

    saved_tpv = {}

    # Loop Forever
    while True:

        # Read Next UDP Packet
        data, addr = sock.recvfrom(65535) # UDP buffer size
        payload = json.loads(data.decode())

        # ---------VVV----------------VVV-------
        #
        # TODO: Add code here to analyze the packet
        #       For example, when you receive a TPV packet, record the GPS location
        #                    then when an IMU packet arrives, determine if it's a
        #                    bump or not, and use the stored GPS location to
        #                    mark it.

        if payload['class'] == 'TPV':
            saved_tpv.update(payload)
        elif payload['class'] == 'POI':
            payload['time'] = saved_tpv['time']
            payload['lat'] = saved_tpv['lat']
            payload['lon'] = saved_tpv['lon']
            payload['alt'] = saved_tpv['alt']
            payload['mileage'] = saved_tpv['mileage']

        #
        # ---------^^^----------------^^^-------

        # Forward the Packet
        send_udp(sock, dest_ip, dest_port, payload)

if __name__ == "__main__":
    # read your config
    CONFIG = util.read_config()

    udp_receiver(
        CONFIG['analyzer']['udp']['host'],
        CONFIG['analyzer']['udp']['port'],
        CONFIG['web']['udp']['host'],
        CONFIG['web']['udp']['port'],
    )
