#!/usr/bin/python3
"""
UNH Capstone 2026 In-Line PiRail Packet Analzyer
"""

import socket

import util
import json

# an estimation based on bump tests conducted in the fall of 2025
ACC_Z_THRESHOLD = 68

ROLLING_RANGE = 25
rolling_acc_x = []
rolling_acc_z = []

ACC_X_OFFSET = -0.7152996666441955 # Used to account for apparent sensor offset. Is mean of measurement during fall 2025 test run.
ACC_Z_OFFSET = 9.8 # To account for gravity

# MLR coefficients
MODEL_CONSTANT = 0.3761
MODEL_SPEED_COEF = 0.4139
MODEL_ACC_X_COEF = 1.1229

ERROR_THRESHOLD = 4.653

REPEATED_POI_PREVENTION_THRESHOLD = 40
entries_since_poi = 0

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

            if is_point_of_interest_mlr(payload):
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

def is_point_of_interest_acc_z_threshold(imu_point) -> bool:
    # 9.81 is acceleration due to gravity
    normalized_acc_z = abs(imu_point['acc_z'] - 9.81)

    if normalized_acc_z > ACC_Z_THRESHOLD:
        return True

    return False

def is_point_of_interest_mlr(imu_point) -> bool:
    rolling_acc_z.append(abs(imu_point['acc_z']  - ACC_Z_OFFSET))
    if len(rolling_acc_z) > ROLLING_RANGE:
        del rolling_acc_z[0]

    rolling_acc_x.append(abs(imu_point['acc_x']  - ACC_X_OFFSET))
    if (len(rolling_acc_x) > ROLLING_RANGE):
        del rolling_acc_x[0]

    acc_z_normalized_rolling_magnitude = sum(rolling_acc_z) / len(rolling_acc_z)
    acc_x_normalized_rolling_magnitude = sum(rolling_acc_x) / len(rolling_acc_x)

    acc_z_pred = MODEL_CONSTANT + (acc_x_normalized_rolling_magnitude * MODEL_ACC_X_COEF) + (imu_point['speed'] * MODEL_SPEED_COEF)

    absolute_error = abs(acc_z_normalized_rolling_magnitude - acc_z_pred)

    is_potential_POI = absolute_error > ERROR_THRESHOLD

    if (is_potential_POI):
        if entries_since_POI < REPEATED_POI_PREVENTION_THRESHOLD:
            is_potential_POI = False
        entries_since_POI = 0
    else:
        entries_since_POI += 1

    return is_potential_POI



if __name__ == "__main__":
    # read your config
    CONFIG = util.read_config()

    udp_receiver(
        CONFIG['analyzer']['udp']['host'],
        CONFIG['analyzer']['udp']['port'],
        CONFIG['web']['udp']['host'],
        CONFIG['web']['udp']['port'],
    )
