#!/usr/bin/python3
"""
Sample In-Line PiRail Packet Analzyer
"""

import socket

import util
import json

# 40 is an estimation based on bump tests conducted in the fall of 2025
ACC_Z_THRESHOLD = 68

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
        #        When you receive a TPV packet, record the GPS location
        #                    then when an IMU packet arrives, determine if it's a
        #                    bump or not, and use the stored GPS location to
        #                    mark it.
        #

        if payload['class'] == 'ATT': # imu_logger.py outputs ATT (vehicle-attitude) entries
            payload['speed'] = saved_tpv.get('speed', 0)

            if is_point_of_interest(payload):
                payload['class'] = 'POI'

                payload['time'] = saved_tpv['time']
                payload['lat'] = saved_tpv['lat']
                payload['lon'] = saved_tpv['lon']
                payload['alt'] = saved_tpv['alt']
                payload['mileage'] = saved_tpv['mileage']

        elif payload['class'] == 'TPV': #gps_logger.py outputs TPV (time-position-velocity) entries
            saved_tpv.update(payload)

        elif payload['class'] == 'POI':
            payload['time'] = saved_tpv['time']
            payload['lat'] = saved_tpv['lat']
            payload['lon'] = saved_tpv['lon']
            payload['alt'] = saved_tpv['alt']
            payload['mileage'] = saved_tpv['mileage']
            
        # Forward the Packet
        send_udp(sock, dest_ip, dest_port, payload)

def is_point_of_interest(imu_point) -> bool: 
    # 9.81 is acceleration due to gravity
    normalized_acc_z = abs(imu_point['acc_z'] - 9.81)

    if normalized_acc_z > ACC_Z_THRESHOLD:
        return True

    return False

if __name__ == "__main__":
    # read your config
    CONFIG = util.read_config()

    udp_receiver(
        CONFIG['analyzer']['udp']['host'],
        CONFIG['analyzer']['udp']['port'],
        CONFIG['web']['udp']['host'],
        CONFIG['web']['udp']['port'],
    )

