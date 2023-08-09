"""
Driver Module for the HPS3D160
"""
import sys
import threading
import time
import signal
import datetime
import json
import serial

import crc16


def bytes_to_hex(buff):
    """
    Convert bytes to a hex string
    """
    out = []
    for i in buff:
        out.append("%02x" % i)
    return out

def bytes_to_short(buff):
    """
    Convert two bytes to short int
    """
    return int(buff[0] + (buff[1] << 8))

def bytes_to_int(buff):
    """
    Convert two bytes to short int
    """
    return int(buff[0] + (buff[1] << 8) + (buff[2] << 16) + (buff[3] << 24))

class Hps3DLidar():
    """
    Driver for HPS 3D 160 LIDAR Scanner
    """
    RESPONSE_FAIL = 0x00
    RESPONSE_SUCCEED = 0x01

    MODE_STANDBY = 0x00
    MODE_SINGLE = 0x01
    MODE_CONTINUOUS = 0x02

    WIDTH = 160
    HEIGHT = 60

    LOW_SIGNAL = 0xff14    # 65300
    OUT_OF_RANGE = 0xff78  # 65400
    OUT_OF_RANGE2 = 0xffdc # 65500
    INVALID_RANGE = 0xfffa # 65530

    def __init__(self, ttyname, address, outputfile=None):
        """
        Initialize and start reading thread
        """
        self.data = {}
        self.outputfile = outputfile
        self.event = threading.Event()
        self.event.clear()
        if ttyname is not None:
            self.ser = serial.Serial(ttyname, timeout=5)
            self.address = address
            self.thread = threading.Thread(target=self.read, args=())
            self.thread.start()

    def done(self):
        """
        Kill the reading thread
        """
        self.event.set()
        self.thread.join()
        print("exiting")

    def read_address(self):
        """
        Command #1: Read Address
        """
        buff = b'\xf5\x0a\x05\xba\xff\x02\x1f\xd6'
        #print("out:", buff)
        self.ser.write(buff)


    def decode_read(self, buff):
        """
        Decode Read Address Response
        """
        retval = {
            'address': buff[4],
            'rid': buff[5],
            'success': buff[6] == Hps3DLidar.RESPONSE_SUCCEED,
            }
        return retval

    def set_address(self, new_address):
        """
        Command #2: Set Address
        """
        if not 0x00 <= new_address <= 0xfe:
            raise Exception("Bad Value")
        buff = bytearray(b'\xf5\x0a\x06\xba\x00\x01\x00\x00\x00')
        buff[4] = self.address
        buff[6] = new_address
        crc = crc16.ccitt(buff[3:7])
        buff[7] = crc & 0xff
        buff[8] = (crc >> 8) & 0xff
        #print("out:", buff)
        self.ser.write(buff)

    def read_version(self):
        """
        Command #3: Read Version
        """
        buff = bytearray(b'\xf5\x0a\x04\xa0\x00\x00\x00')
        buff[4] = self.address
        crc = crc16.ccitt(buff[3:5])
        buff[5] = crc & 0xff
        buff[6] = (crc >> 8) & 0xff
        #print("out:", buff)
        self.ser.write(buff)

    def decode_read_version(self, buff):
        """
        Decode Version Response
        """
        retval = {
            'address': buff[4],
            'rid': buff[5],
            'year': buff[6] + 2000,
            'month': buff[7],
            'day': buff[8],
            'major': buff[9],
            'minor': buff[10],
            'revision': buff[11],
            }
        retval['version'] = "%04d-%02d-%02d V%d.%d Rev%d" % (
                retval['year'],
                retval['month'],
                retval['day'],
                retval['major'],
                retval['minor'],
                retval['revision'],
                )
        return retval

    def read_serial(self):
        """
        Command #4: Read Serial
        """
        buff = bytearray(b'\xf5\x0a\x05\xa1\x00\x02\x00\x00')
        buff[4] = self.address
        crc = crc16.ccitt(buff[3:6])
        buff[6] = crc & 0xff
        buff[7] = (crc >> 8) & 0xff
        #print("out:", buff)
        self.ser.write(buff)

    def decode_read_serial(self, buff):
        """
        Decode Serial Number Response
        """
        retval = {
            'address': buff[4],
            'rid': buff[5],
            'serial': "",
        }
        for i in range(6,67,1):
            if buff[i] == 0:
                break
            retval['serial'] += "%c" % buff[i]
        return retval

    def set_working_mode(self, mode):
        """
        Command #5: Set Working Mode
        """
        buff = bytearray(b'\xf5\x0a\x06\xa3\x00\x01\x00\x00\x00')
        buff[4] = self.address
        buff[6] = mode & 0xff
        crc = crc16.ccitt(buff[3:7])
        buff[7] = crc & 0xff
        buff[8] = (crc >> 8) & 0xff
        #print("out:", buff)
        self.ser.write(buff)

    def decode_set_working_mode(self, buff):
        """
        Decode Set Working Mode Response
        """
        retval = {
            'address': buff[4],
            'rid': buff[5],
            'success': buff[6] == Hps3DLidar.RESPONSE_SUCCEED,
        }
        return retval

    def select_group(self, group_id):
        """
        Command #6: Select Group
        """
        buff = bytearray(b'\xf5\x0a\x06\xac\x00\xa9\x00\x00\x00')
        buff[4] = self.address
        buff[6] = group_id & 0xff
        crc = crc16.ccitt(buff[3:7])
        buff[7] = crc & 0xff
        buff[8] = (crc >> 8) & 0xff
        #print("out:", buff)
        self.ser.write(buff)

    def decode_select_group(self, buff):
        """
        Decode Select Group Response
        """
        buff = self.read_data()
        retval = {
            'address': buff[4],
            'rid': buff[5],
            'success': buff[6] == Hps3DLidar.RESPONSE_SUCCEED,
        }
        return retval

    def read_group_id(self):
        """
        Command #7: Read Group Id
        """
        buff = bytearray(b'\xf5\x0a\x05\xac\x00\xaa\x00\x00')
        buff[4] = self.address
        crc = crc16.ccitt(buff[3:6])
        buff[6] = crc & 0xff
        buff[7] = (crc >> 8) & 0xff
        #print("out:", buff)
        self.ser.write(buff)

    def decode_read_group_id(self, buff):
        """
        Decode Group Id Response
        """
        retval = {
            'address': buff[4],
            'rid': buff[5],
            'group_id': buff[6],
        }
        return retval

    def read_data(self, mode="binary"):
        """
        Read Data from Serial Device
        """

        h1 = self.ser.read(1)
        h2 = self.ser.read(1)

        # Try to sync
        while h1 != b'\xf5' and h2 != b'\x5f':
            h1 = h2
            h2 = self.ser.read(1)

        header = h1 + h2
        if len(header) != 2:
            return None
        if header != b'\xf5\x5f':
            raise Exception("Bad Header")
        length = self.ser.read(2)
        data = self.ser.read(bytes_to_short(length)-4)
        crc = self.ser.read(2)
        if crc16.ccitt(data) != bytes_to_short(crc):
            raise Exception("CRC Mismatch")
        end = self.ser.read(2)
        if end != b'\x5f\xf5':
            raise Exception("Bad Message End")
        if mode == "binary":
            message = header + length + data + crc + end
        elif mode == "json":
            message = {
                'header': header,
                'length': length,
                'address': data[0],
                'rid': data[1],
                'data': data[2:],
                'crc': crc,
                'end': end,
            }
        else:
            raise Exception("Bad Mode Request")
        return message

    def read(self, filename=None):
        """
        Read Thread
        """
        decoders = {
                0x18: self.decode_detailed,
                0xa0: self.decode_read_version,
                0xa1: self.decode_read_serial,
                0xa3: self.decode_set_working_mode,
                0xac: self.decode_read_group_id,
                0xba: self.decode_read,
        }
        if filename is not None:
            with open(filename, "rb") as f:
                buff = f.read()
                retval = decoders[buff[5]](buff)
                retval.update({
                    'class': 'LIDAR3D',
                    'device': 'HPS3D160',
                    'filename': filename,
                    'time': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                })
            return retval

        while not self.event.isSet():
            buff = self.read_data()
            if buff is None:
                continue
            #print("in:", buff)
            retval = decoders[buff[5]](buff)
            retval.update({
                'class': 'LIDAR3D',
                'device': 'HPS3D160',
                'time': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            })
            if self.outputfile is not None:
                self.outputfile.write("%s %s %s *\n" % (retval['time'], retval['class'], json.dumps(retval)))
                self.outputfile.flush()
                self.data = retval
            else:
                print(json.dumps(retval))
            #time.sleep(1)
        return retval

    def decode_detailed(self, data):
        """
        Decode Detailed Data Frame
        """
        retval = {
            'dummy': bytes_to_short(data[6:8]),
            'average_distance_mm': bytes_to_short(data[8:10]),
            'valid_signal_strength': bytes_to_short(data[10:12]),
            'average_signal_strength': bytes_to_short(data[12:14]),
            'num_weak_pixels': bytes_to_short(data[14:16]),
            'num_saturated_pixels': bytes_to_short(data[16:18]),
            'maximum_distance': bytes_to_short(data[18:20]),
            'minimum_distance': bytes_to_short(data[20:22]),
            'data_frame_counter': bytes_to_int(data[22:26]),
            'reserved': bytes_to_int(data[26:30]),
            'depth': [],
        }
        index = 30
        for row in range(Hps3DLidar.HEIGHT):
            depth_array = []
            for pixel in range(Hps3DLidar.WIDTH):
                depth = bytes_to_short(data[index:index+2])
                index += 2
                depth_array.append(depth)
            retval['depth'].append(depth_array)
        return retval


if __name__ == "__main__":
    lidar = Hps3DLidar("/dev/ttyACM0", 0, None)
    lidar.set_address(0)
    lidar.read_address()
    lidar.read_version()
    lidar.read_serial()
    lidar.read_group_id()
    lidar.set_working_mode(Hps3DLidar.MODE_SINGLE)
    time.sleep(10)
    lidar.done()
    #lidar = Hps3DLidar(None, 0)
    #print(lidar.read(filename=sys.argv[1]))
