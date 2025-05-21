#!/usr/bin/env python3
"""
Interface for the Wit-Motion JY-GPSIMU Serial Device
"""

import threading
import time
import serial
import json
import math
import socket

RETURN_CONTEXT = b'\xFF\xAA\x02\xFF\x07'
SAVE = b'\xFF\xAA\x00\x00\x00'

def cvt_lat_lon(value):
    """ convert to floating point value """
    d = int(value / 10000000)
    m = (value - d * 10000000) / 100000
    return d + m / 60

def do_output(fileptr, obj):
    if fileptr is None:
        return

    if 'time' in obj and 'class' in obj:
        try:
            fileptr.write(obj['time'])
            fileptr.write(" ")
            fileptr.write(obj['class'])
            fileptr.write(" ")
            fileptr.write(json.dumps(obj))
            fileptr.write(" *\n")
        except ValueError:
            pass

def send_udp(sock, ip, port, obj):
    """ Send Packet """
    sock.sendto(json.dumps(obj).encode(), (ip, port))

class WitMotionJyGpsImu():
    """ Wit-Motion JY-GPSIMU Class """

    def __init__(self, ttyname, gpsout, imuout, config):
        """ Initialize """
        self.event = threading.Event()
        self.event.clear()
        self.ttyname = ttyname
        self.gpsout = gpsout
        self.imuout = imuout
        self.imu_device = 'WTGAHRS1'
        self.thread = threading.Thread(target=self.read, args=(self.event,))
        self.thread.start()
        self.wit = {}
        self.config = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.imux = config['imu']['x']
        self.imuy = config['imu']['y']
        self.imuz = config['imu']['z']

    def update_config(self, config):
        self.config = config

    def done(self):
        """ Call when done """
        self.event.set()
        self.thread.join()

    def decode(self, s, t, d, c):
        """ Decode a byte stream """
        if t == b'\x50':
            year = int.from_bytes(d[0:1],"little")
            month = int.from_bytes(d[1:2],"little")
            day = int.from_bytes(d[2:3],"little")
            hh = int.from_bytes(d[3:4],"little")
            mm = int.from_bytes(d[4:5],"little")
            ss = int.from_bytes(d[5:6],"little")
            ms = int.from_bytes(d[6:8],"little")
            #print("Time",year,month,day,hh,mm,ss,ms)
            self.wit['time'] = "%4d-%02d-%02dT%02d:%02d:%02d.%03dZ" % (year+2000, month, day, hh, mm, ss, ms)
            #outfile.write("Time %s\n" % self.wit['time'])
            obj = self.get_sky()
            send_udp(self.sock, self.config['udp']['ip'], self.config['udp']['port'], obj)
            if self.config['gps']['logging']:
                do_output(self.gpsout,obj)

            obj = self.get_tpv()
            send_udp(self.sock, self.config['udp']['ip'], self.config['udp']['port'], obj)
            if self.config['gps']['logging']:
                do_output(self.gpsout,obj)

            obj = self.get_att()
            send_udp(self.sock, self.config['udp']['ip'], self.config['udp']['port'], obj)
            if self.config['imu']['logging']:
                do_output(self.imuout,obj)
        elif t == b'\x51':
            ax = 9.8*16*float(int.from_bytes(d[0:2],"little", signed=True))/32768.0
            ay = 9.8*16*float(int.from_bytes(d[2:4],"little", signed=True))/32768.0
            az = 9.8*16*float(int.from_bytes(d[4:6],"little", signed=True))/32768.0
            t = float(int.from_bytes(d[6:8],"little", signed=True))/100.0
            #print("Accel",ax,ay,az,t)
            self.wit['ACCx'] = ax
            self.wit['ACCy'] = ay
            self.wit['ACCz'] = az
            self.wit['temp'] = t
            #outfile.write("Accel %f %f %f %f\n" % (ax,ay,az,t))
        elif t == b'\x52':
            wx = 2000*float(int.from_bytes(d[0:2],"little", signed=True))/32768.0
            wy = 2000*float(int.from_bytes(d[2:4],"little", signed=True))/32768.0
            wz = 2000*float(int.from_bytes(d[4:6],"little", signed=True))/32768.0
            t = float(int.from_bytes(d[6:8],"little", signed=True))/100.0
            #print("Angluar",wx,wy,wz,t)
            self.wit['GYRx'] = wx
            self.wit['GYRy'] = wy
            self.wit['GYRz'] = wz
            self.wit['temp'] = t
            #outfile.write("Angluar %f %f %f %f\n" % (wx,wy,wz,t))
        elif t == b'\x53':
            roll = 180.0*float(int.from_bytes(d[0:2],"little", signed=True))/32768.0
            pitch = 180.0*float(int.from_bytes(d[2:4],"little", signed=True))/32768.0
            yaw = 180.0*float(int.from_bytes(d[4:6],"little", signed=True))/32768.0
            version = int.from_bytes(d[6:8],"little", signed=True)
            #print("Angle",roll,pitch,yaw,version)
            self.wit['ANGx'] = pitch + self.config['imu']['pitch_adj']
            self.wit['ANGy'] = roll + self.config['imu']['roll_adj']
            self.wit['ANGz'] = yaw + self.config['imu']['yaw_adj']
            #outfile.write("Angle %f %f %f\n" % (pitch,roll,yaw))
        elif t == b'\x54':
            hx = int.from_bytes(d[0:2],"little", signed=True)
            hy = int.from_bytes(d[2:4],"little", signed=True)
            hz = int.from_bytes(d[4:6],"little", signed=True)
            t = float(int.from_bytes(d[6:8],"little", signed=True))/100.0
            #print("Magnetic",hx,hy,hz,t)
            self.wit['MAGx'] = hx
            self.wit['MAGy'] = hy
            self.wit['MAGz'] = hz
            self.wit['temp'] = t
            #outfile.write("Magnetic %f %f %f %f\n" % (hx,hy,hz,t))
        elif t == b'\x55':
            d0 = int.from_bytes(d[0:2],"little", signed=True)
            d1 = int.from_bytes(d[2:4],"little", signed=True)
            d2 = int.from_bytes(d[4:6],"little", signed=True)
            d3 = int.from_bytes(d[6:8],"little", signed=True)
            #print("Port",d0,d1,d2,d3)
        elif t == b'\x56':
            p = int.from_bytes(d[0:4],"little", signed=True)
            h = int.from_bytes(d[4:8],"little", signed=True) / 100.0 # convert to m
            #print("Pressure",p,h)
            self.wit['alt'] = h
            #outfile.write("Pressure %d\n" % (h))
        elif t == b'\x57':
            lon = cvt_lat_lon(int.from_bytes(d[0:4],"little",signed=True))
            lat = cvt_lat_lon(int.from_bytes(d[4:8],"little",signed=True))
            #print ("Location",lat, lon)
            self.wit['lat'] = lat
            self.wit['lon'] = lon
            #outfile.write("Location %f %f\n" % (lat,lon))
        elif t == b'\x58':
            gpsh = float(int.from_bytes(d[0:2],"little",signed=True))/10.0
            gpsy = float(int.from_bytes(d[2:4],"little",signed=True))/10.0
            gpsv = float(int.from_bytes(d[4:8],"little",signed=True))/1000.0
            #print ("GroundSpeed", gpsh, gpsy, gpsv)
            self.wit['alt'] = gpsh
            self.wit['track'] = gpsy
            self.wit['speed'] = gpsv
            #outfile.write("Groundspeed %f %f %f\n" % (gpsh, gpsy, gpsv))
        elif t == b'\x59':
            q0 = float(int.from_bytes(d[0:2],"little",signed=True))/32768.0
            q1 = float(int.from_bytes(d[2:4],"little",signed=True))/32768.0
            q2 = float(int.from_bytes(d[4:6],"little",signed=True))/32768.0
            q3 = float(int.from_bytes(d[6:8],"little",signed=True))/32768.0
            #print ("Quaternion",q0,q1,q2,q3)
        elif t == b'\x5a':
            sn = int.from_bytes(d[0:2],"little",signed=True)
            pdop = float(int.from_bytes(d[2:4],"little",signed=True))/32768.0
            hdop = float(int.from_bytes(d[4:6],"little",signed=True))/32768.0
            vdop = float(int.from_bytes(d[6:8],"little",signed=True))/32768.0
            self.wit['nsat'] = sn
            self.wit['usat'] = sn
            self.wit['pdop'] = pdop
            self.wit['hdop'] = hdop
            self.wit['vdop'] = vdop
            #print ("Accuracy",sn,pdop,hdop,vdop)
            #outfile.write("Accuracy %d %f %f %f\n" % (sn, pdop, hdop, vdop))
        else:
            #print ("Unknown", s.hex(), t.hex(), d.hex(), c.hex())
            pass

    def read(self, event):
        """ Read from the serial port """
        ser = serial.Serial(self.ttyname)
        self.gps['device'] = ser.name
        #ser.write(RETURN_CONTEXT)
        #ser.flush()
        #ser.write(SAVE)
        #ser.flush()
        while not event.isSet():
            s = ser.read(1)
            if s != b'\x55':
                continue

            t = ser.read(1)
            d = ser.read(8)
            c = ser.read(1)

            chksum = s[0] + t[0]
            for i in d:
                chksum += i
            chksum %= 256

            if int.from_bytes(c,"little") == chksum:
                #print("chksum ok")
                self.decode(s,t,d,c)
            else:
                #print("chksum bad")
                pass

        ser.close()

    def get_sky(self):
        sky = {
            'class': 'SKY',
        }
        try:
            sky.update({
                'device': self.wit['device'],
                'time': self.wit['time'],
                'pdop': self.wit['pdop'],
                'hdop': self.wit['hdop'],
                'vdop': self.wit['vdop'],
                'nSat': self.wit['nsat'],
                'uSat': self.wit['usat'],
                'satellites': [{'used': True}] * self.wit['usat'],
            })
        except KeyError:
            pass
        return sky

    def get_tpv(self):
        tpv = {
            'class': 'TPV',
            'mode': 0,
            'status': 0,
        }
        try:
            tpv.update({
                'device': self.wit['device'],
                'time': self.wit['time'],
                'lat': self.wit['lat'],
                'lon': self.wit['lon'],
                'alt': self.wit['alt'],
                'track': self.wit['track'],
                'speed': self.wit['speed'],
            })
            if 'usat' in self.wit:
                tpv['status'] = 1
                if self.wit['usat'] > 0:
                    tpv['mode'] = min(3, self.wit['usat'])
                else:
                    tpv['mode'] = 1
        except KeyError:
            pass
        return tpv

    def get_att(self):
        att = {
            'class': 'ATT',
        }
        try:
            att.update({
                'device': self.imu_device,
                'time': self.wit['time'],
                'acc_x': self.wit['ACC'+self.imux],
                'acc_y': self.wit['ACC'+self.imuy],
                'acc_z': self.wit['ACC'+self.imuz],
                'gyro_x': self.wit['GYR'+self.imux],
                'gyro_y': self.wit['GYR'+self.imuy],
                'gyro_z': self.wit['GYR'+self.imuz],
                'mag_x': self.wit['MAG'+self.imux],
                'mag_y': self.wit['MAG'+self.imuy],
                'mag_z': self.wit['MAG'+self.imuz],
                'pitch': self.wit['ANG'+self.imux],
                'pitch_st': "N",
                'roll': self.wit['ANG'+self.imuy],
                'roll_st': "N",
                'yaw': self.wit['ANG'+self.imuz],
                'yaw_st': "N",
                'temp': self.wit['temp'],
            })
            # Calculate Heading
            att['heading'] = (math.degrees(math.atan2(att['mag_y'], att['mag_x'])) - 90) % 360
            # Calculate vector length
            att['acc_len'] = math.sqrt(att['acc_x']**2+att['acc_y']**2+att['acc_z']**2)
            att['mag_len'] = math.sqrt(att['mag_x']**2+att['mag_y']**2+att['mag_z']**2)
            att['mag_st'] = "N"
        except KeyError:
            pass
        return att

    def next(self):
        """ Yield the Next Result """
        last_time = ""
        last_lat = last_lon = last_alt = 0
        while True:
            if 'time' in self.wit:
                if last_time != self.wit['time']:
                    last_time = self.wit['time']
                    yield_data = []

                    if self.wit['lat'] != last_lat or self.wit['lon'] != last_lon or self.wit['alt'] != last_alt:
                        last_lat = self.wit['lat']
                        last_lon = self.wit['lon']
                        last_alt = self.wit['alt']

                        sky = {
                            'class': 'SKY',
                            'time': self.wit['time'],
                            'device': self.wit['device'],
                            'pdop': self.wit['pdop'],
                            'hdop': self.wit['hdop'],
                            'vdop': self.wit['vdop'],
                            'nSat': self.wit['nsat'],
                            'uSat': self.wit['usat'],
                            'satellites': [{'used': True}] * self.wit['usat'],
                        }
                        yield_data.append((sky['time'], "SKY", sky))

                        tpv = {
                            'class': 'TPV',
                            'device': self.wit['device'],
                            'mode': 0,
                            'status': 0,
                            'time': self.wit['time'],
                            'lat': self.wit['lat'],
                            'lon': self.wit['lon'],
                            'alt': self.wit['alt'],
                            'track': self.wit['track'],
                            'speed': self.wit['speed'],
                        }
                        if 'sn' in self.wit:
                            tpv['status'] = 1
                            if self.wit['usat'] > 0:
                                tpv['mode'] = min(3, self.wit['usat']) 
                            else:
                                tpv['mode'] = 1

                        yield_data.append((tpv['time'], "TPV", tpv))

                    att = self.get_att()
                    yield_data.append((att['time'], "ATT", att))
                    yield yield_data
            else:
                time.sleep(5)

if __name__ == "__main__":
    config = {
        "gps": {"logging": True},
        "imu": {"logging": True},
    }
    with open("gpslog.csv", "w") as gpsout:
        with open("imulog.csv", "w") as imuout:
            W = WitMotionJyGpsImu("/dev/ttyUSB0", gpsout, imuout, config)

            try:
                while True:
                    #print(W.get_sky())
                    #print(W.get_tpv())
                    #print(W.get_att())
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

            W.done()
