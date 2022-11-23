#!/usr/bin/env python
"""Bluetooth motion tracker module.
Copyright 2017 Mark Mitterdorfer
Class to read from a Bluetooth MPU6050 device.
Obtain acceleration, angular velocity, angle and temperature
"""

import os
import threading
import struct
import bluetooth
import datetime
import json
import time
import util

VERSION = 9

MAC = "20:19:06:25:18:92"

class MotionTracker(object):
    """Class to track movement from MPU6050 Bluetooth device.
    """
    device = "MPU6050"

    def __init__(self, bd_addr, port=1):
        """Initialization for tracker object.
        Args:
            bd_addr (str) : Bluetooth address
            port (int, optional) : Port, defaults to 1
        Attributes:
            bd_addr (str): Bluetooth address
            port (int): Port
            sock (bluetooth.bluez.BluetoothSocket) : Bluetooth socket object
            acc_x (float) : acceleration in X
            acc_y (float) : acceleration in Y
            acc_z (float) : acceleration in Z
            angv_x (float) : angular velocity in X
            angv_y (float) : angular velocity in Y
            angv_z (float) : angular velocity in Z
            ang_x (float) : angle degrees in X
            ang_y (float) : angle degrees in Y
            ang_z (float) : angle degrees in Z
            temperature (float) : temperature in degrees celsius
            __thread_read_device_data (threading.Thread) : Read input thread
        """
        self.bd_addr = bd_addr
        self.port = port

        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.connect((self.bd_addr, self.port))

        self.acc_x = 0.0
        self.acc_y = 0.0
        self.acc_z = 0.0

        self.angv_x = 0.0
        self.angv_y = 0.0
        self.angv_z = 0.0

        self.ang_x = 0.0
        self.ang_y = 0.0
        self.ang_z = 0.0

        self.temperature = 0.0
        self.__thread_read_device_data = None

    def start_read_data(self):
        """Start reading from device. Wait for a second or two before
        reading class attributes to allow values to 'settle' in.
        Non blocking I/O performed via a private read thread.
        """

        self.__thread_read_device_data = threading.Thread(target=self.__read_device_data)
        self.__thread_read_device_data.is_running = True
        self.__thread_read_device_data.start()

    def stop_read_data(self):
        """Stop reading from device. Join back to main thread and
        close the socket.
        """

        self.__thread_read_device_data.is_running = False
        self.__thread_read_device_data.join()
        self.sock.close()

    def __read_device_data(self):
        """Private method to read device data in 9 byte blocks.
        """

        while self.__thread_read_device_data.is_running:
            data_block = self.sock.recv(1)
            if data_block == b'\x55':
                data_block_type = self.sock.recv(1)
                # Acceleration
                if data_block_type == b'\x51':
                    # Read 9 byte block
                    ax_l = self.sock.recv(1)
                    ax_h = self.sock.recv(1)
                    ay_l = self.sock.recv(1)
                    ay_h = self.sock.recv(1)
                    az_l = self.sock.recv(1)
                    az_h = self.sock.recv(1)
                    t_l = self.sock.recv(1)
                    t_h = self.sock.recv(1)
                    self.sock.recv(1) # Check sum, ignore

                    self.acc_x = struct.unpack("<h", ax_l + ax_h)[0] / 32768.0 * 16.0
                    self.acc_y = struct.unpack("<h", ay_l + ay_h)[0] / 32768.0 * 16.0
                    self.acc_z = struct.unpack("<h", az_l + az_h)[0] / 32768.0 * 16.0
                    self.temperature = struct.unpack("<h", t_l + t_h)[0] / 340.0 + 36.25
                # Angular velocity
                elif data_block_type == b'\x52':
                    # Read 9 byte block
                    wx_l = self.sock.recv(1)
                    wx_h = self.sock.recv(1)
                    wy_l = self.sock.recv(1)
                    wy_h = self.sock.recv(1)
                    wz_l = self.sock.recv(1)
                    wz_h = self.sock.recv(1)
                    t_l = self.sock.recv(1)
                    t_h = self.sock.recv(1)
                    self.sock.recv(1)  # Check sum, ignore

                    self.angv_x = struct.unpack("<h", wx_l + wx_h)[0] / 32768.0 * 2000.0
                    self.angv_y = struct.unpack("<h", wy_l + wy_h)[0] / 32768.0 * 2000.0
                    self.angv_z = struct.unpack("<h", wz_l + wz_h)[0] / 32768.0 * 2000.0
                    self.temperature = struct.unpack("<h", t_l + t_h)[0] / 340.0 + 36.25
                # Angle
                elif data_block_type == b'\x53':
                    # Read 9 byte block
                    roll_l = self.sock.recv(1)
                    roll_h = self.sock.recv(1)
                    pitch_l = self.sock.recv(1)
                    pitch_h = self.sock.recv(1)
                    yaw_l = self.sock.recv(1)
                    yaw_h = self.sock.recv(1)
                    t_l = self.sock.recv(1)
                    t_h = self.sock.recv(1)
                    self.sock.recv(1)  # Check sum, ignore

                    self.ang_x = struct.unpack("<h", roll_l + roll_h)[0] / 32768.0 * 180.0
                    self.ang_y = struct.unpack("<h", pitch_l + pitch_h)[0] / 32768.0 * 180.0
                    self.ang_z = struct.unpack("<h", yaw_l + yaw_h)[0] / 32768.0 * 180.0
                    self.temperature = struct.unpack("<h", t_l + t_h)[0] / 340.0 + 36.25

def main(output_directory):
    """Test driver stub.
    """

    config = {
        "class": "CONFIG",
        "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "imu": {"log": True, "x": "x", "y": "y", "z": "z"},
    }

    # Create output directory
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    # Create output file
    with open(os.path.join(output_directory, datetime.datetime.now().strftime("%Y%m%d%H%M")+"_imu.csv"), "w") as imu_output:
        util.write_header(imu_output, config)

        try:
            session = MotionTracker(bd_addr=MAC)
            session.start_read_data()

            while True:
                now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                temp_obj = {
                    "ang_"+config['imu']['x']: session.ang_x,
                    "ang_"+config['imu']['y']: session.ang_y,
                    "ang_"+config['imu']['z']: session.ang_z,
                }
                obj = {
                    "class": "ATT",
                    "time": now,
                    "device": session.device,
                    "acc_"+config['imu']['x']: session.acc_x,
                    "acc_"+config['imu']['y']: session.acc_y,
                    "acc_"+config['imu']['z']: session.acc_z,
                    "gyro_"+config['imu']['x']: session.angv_x,
                    "gyro_"+config['imu']['y']: session.angv_y,
                    "gyro_"+config['imu']['z']: session.angv_z,
                    "yaw": temp_obj['ang_z'],
                    "yaw_st": "N",
                    "pitch": temp_obj['ang_x'],
                    "pitch_st": "N",
                    "roll": temp_obj['ang_y'],
                    "roll_st": "N",
                    "temp": session.temperature,
                }
                imu_output.write("%s %s %s *\n" % (obj['time'], obj['class'], json.dumps(obj)))
                time.sleep(0.02)

        except KeyboardInterrupt:
            session.stop_read_data()


if __name__ == "__main__":
    main("/root/gps-data")
