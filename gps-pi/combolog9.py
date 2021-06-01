#!/usr/bin/python3
"""
GPS / ACCEL LIDAR Logger V9
"""

import os
import sys
import threading
import time
import datetime
import gps
import json
import nmea
import statistics
from http.server import BaseHTTPRequestHandler, HTTPServer

import imu_logger

from rplidar import RPLidar

#import adxl345_shim as accel
import berryimu_shim as accel

HOST_NAME = ''
PORT_NUMBER = 80

ALWAYS_LOG = True

ERROR_DELAY = 10
SYNC_DELAY = 5
IDLE_DELAY = 60

# Configure Axis
try:
    with open("config.json", "r") as f:
        CONFIG = json.loads(f.read())
except:
    CONFIG = {
        "imu": {"log": True, "x": "x", "y": "y", "z": "z"},
        "gps": {"log": True},
        "lidar": {"log": True},
        "audio": {"log": True},
    }

CONFIG['class'] = "CONFIG"
CONFIG['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

class MyHandler(BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        global CURRENT
        global DONE
        global RESTART
        global HOLD
        global MEMO

        content_type = "text/html; charset=utf-8"

        if s.path == "/poweroff":
            content_type = "application/json"
            output = "{\"message\": \"Shutting down...\"}"
            DONE = True
            RESTART = False
            os.system("shutdown --poweroff +1")
        elif s.path == "/reset":
            content_type = "application/json"
            output = "{\"message\": \"Resetting...\"}"
            DONE = True
        elif s.path.startswith("/mark?memo="):
            HOLD = 1
            MEMO = s.path.replace("/mark?memo=", "")
            content_type = "application/json"
            output = "{\"message\": \"Marked...\"}"
        elif s.path.startswith("/hold?memo="):
            HOLD = 15 
            MEMO = s.path.replace("/hold?memo=", "")
            content_type = "application/json"
            output = "{\"message\": \"Holding...\"}"
        elif s.path.startswith("/setup?"):
            for var in s.path.split("?")[1].split("&"):
                key, value = var.split("=")
                CONFIG['imu'][key]=value.lower()
            content_type = "application/json"
            output = "{\"message\": \"Stored...\"}"
            with open("config.json", "w") as f:
                CONFIG['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                f.write(json.dumps(CONFIG))
            DONE = True
        elif s.path == "/lidar":
            content_type = "application/json"
            output = json.dumps(LIDAR_DATA)
        elif s.path == "/gps":
            content_type = "application/json"
            output ="\"temp\": %f" % TEMP
            output +=",\"gps_status\": %d" % GPS_STATUS
            output +=",\"gps_num_sat\": %d" % GPS_NUM_SAT
            output +=",\"gps_num_used\": %d" % GPS_NUM_USED
            output +=(",\"acc_status\": %s" % ACC_STATUS).lower()
            output +=(",\"lidar_status\": %s" % LIDAR_STATUS).lower()
            output +=(",\"hold\": %s" % HOLD).lower()
            # Floating Point Fields
            for key in [
                    'lat', 'epy',
                    'lon', 'epx',
                    'alt', 'epv',
                    'speed', 'eps',
                    'ept',
                    ]:
                if key in CURRENT:
                    output += ",\""+key+"\": " + str(CURRENT[key])

            # Strings Fields
            for key in ['time']:
                if key in CURRENT:
                    output += ",\"gps"+key+"\": \"%s\"" % CURRENT[key]

            output += ",\"time\": \"" + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ") + "\""

            output = "{" + output + "}"
        elif s.path == "/jquery-3.4.1.min.js":
            with open("jquery-3.4.1.min.js", "r") as j:
                output = j.read()
        elif s.path == "/lidar.html":
            with open("lidar.html", "r") as j:
                output = j.read()
        elif s.path == "/gps.html":
            with open("gps.html", "r") as j:
                output = j.read()
        elif s.path == "/setup.html":
            with open("setup.html", "r") as j:
                output = j.read()
        elif s.path == "/favicon.ico":
            output = ""
        else:
            output = "<html><head><title>RPi/GPS/IMU</title></head>"
            output += "<body>"
            output += "<p>You accessed path: %s</p>" % s.path
            output += "</body></html>"

        s.send_response(200)
        s.send_header("Content-type", content_type)
        s.send_header("Content-length", str(len(output)))
        s.end_headers()
        s.wfile.write(output.encode('utf-8'))

def web_server(httpd):
    global DONE
    while not DONE:
        try:
            print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
            httpd.serve_forever()
            print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))
        except KeyboardInterrupt:
            DONE = True
        except Exception as ex:
            print(ex)
        httpd.server_close()

def set_date(gps_date):
    """ Set the system clock """
    sys_date = "%s%s%s%s%s.%s" % (
        gps_date[5:7],
        gps_date[8:10],
        gps_date[11:13],
        gps_date[14:16],
        gps_date[0:4],
        gps_date[17:19])
    command = "date --utc %s > /dev/null" %  sys_date
    os.system(command)

def wait_for_timesync(session):
    """ Wait for Time Sync """
    global CURRENT
    while True:
        try:
            report = session.next()
            if report['class'] != 'TPV':
                continue
            if hasattr(report, 'mode') and report.mode == 1:
                # can't trust a mode=1 time
                continue
            if hasattr(report, 'time'):
                set_date(report.time)
                CURRENT = nmea.tpv_to_json(report)
                return report.time.replace('-', '').replace(':', '').replace('T', '')[0:12]
        except Exception as ex:
            print(ex)
            sys.exit(1)

def mylog(msg):
    logtime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    if isinstance(msg, str):
        msg = {"log": msg}
    print("%s LOG '%s' *" % (logtime, json.dumps(msg)))

def gps_logger(output_directory, session):
    """ GPS Data Logger """
    global INLOCSYNC
    global CURRENT
    global DONE
    global HOLD
    global GPS_STATUS, GPS_NUM_SAT, GPS_NUM_USED

    hold_lat = []
    hold_lon = []
    hold_alt = []

    # Configure
    try:
        with open("config.json", "r") as f:
            config = json.loads(f.read())
    except:
        config = {"class": "CONFIG", "gps": {"log": True}}
    config['time'] =  datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Create the output directory
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    # Open the output file
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    with open(os.path.join(output_directory,timestamp+"_gps.csv"), "w") as gps_output:
        gps_output.write("#v%d\n" % VERSION)
        gps_output.write("%s %s %s *\n" % (config['time'], config['class'], json.dumps(config)))

        while not DONE:
            # GPS
            report = session.next()
            # To see all report data, uncomment the line below
            #print(report)

            if report['class'] == 'TPV':
                obj = nmea.tpv_to_json(report)
                # Add Sat Metrics
                obj['num_sat'] = GPS_NUM_SAT
                obj['num_used'] = GPS_NUM_USED
            elif report['class'] == 'SKY':
                obj = nmea.sky_to_json(report)
                # Add Time
                obj['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                (GPS_NUM_USED, GPS_NUM_SAT) = nmea.calc_used(obj)
            else:
                continue

            # Log the Data
            if 'time' in obj:
                gps_output.write("%s %s %s *\n" % (obj['time'], obj['class'], json.dumps(obj)))

            if obj['class'] == 'TPV':
                if 'mode' in obj:
                    GPS_STATUS = obj['mode']
                    if obj['mode'] == 1:
                        INLOCSYNC = False
                        print("%s Lost location sync" % obj['time'])
                        continue

                if 'lat' in obj and 'lon' in obj and 'time' in obj:
                    CURRENT = obj
                    if not INLOCSYNC:
                        INLOCSYNC = True
                        lastreport = obj
                        print("%s Have location sync" % obj['time'])

                    if HOLD == 0:
                        with open(os.path.join(output_directory,timestamp+"_marks.csv"), "a") as mark:
                            mark_obj = {
                                "class": "MARK",
                                "lat": statistics.mean(hold_lat),
                                "lon": statistics.mean(hold_lon),
                                "num_sat": GPS_NUM_SAT,
                                "num_used": GPS_NUM_USED,
                                "time": obj['time'],
                                "memo": MEMO,
                            }
                            if len(hold_alt) > 0:
                                mark_obj['alt'] = statistics.mean(hold_alt)
                            mark.write("%s %s %s *\n" % (mark_obj['time'], mark_obj['class'], json.dumps(mark_obj)))
                        hold_lat = []
                        hold_lon = []
                        hold_alt = []
                        HOLD = -1
                    elif HOLD > 0:
                        hold_lat.append(report.lat)
                        hold_lon.append(report.lon)
                        if 'alt' in report:
                            hold_alt.append(report.alt)
                        HOLD -= 1

def gps_logger_wrapper(output_directory, session):
    """ Wrapper Around GPS Logger Function """
    global GPS_STATUS

    GPS_STATUS = 0
    try:
        gps_logger(output_directory, session)
    except StopIteration:
        session = None
        mylog("GPSD has terminated")
        DONE = True
    except Exception as ex:
        mylog("GPS Logger Exception: %s" % ex)
    GPS_STATUS = 0
    mylog("GPS done")

def imu_logger_wrapper(output_directory):
    """ Wrapper Around IMU Logger Function """
    global ACC_STATUS
    ACC_STATUS = True
    try:
        imu_logger.imu_logger(output_directory)
    except Exception as ex:
        mylog("IMU Logger Exception: %s" % ex)
    ACC_STATUS = False
    mylog("ACCEL done")

def lidar_logger(output_directory):
    global DONE, LIDAR_STATUS, LIDAR_DATA

    port_name = '/dev/lidar'
    lidar = None

    # Configure
    try:
        with open("config.json", "r") as f:
            config = json.loads(f.read())
    except:
        config = {"class": "CONFIG", "lidar": {"log": True}}
    config['time'] =  datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Create the output directory
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    while not INLOCSYNC:
        time.sleep(SYNC_DELAY)

    while not DONE:
        try:
            lidar = RPLidar(port_name)
            mylog(lidar.get_info())
            mylog(lidar.get_health())
            # Open the output file
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
            with open(os.path.join(output_directory,timestamp+"_lidar.csv"), "w") as lidar_output:
                lidar_output.write("#v%d\n" % VERSION)
                lidar_output.write("%s %s %s *\n" % (config['time'], config['class'], json.dumps(config)))
                for i, scan in enumerate(lidar.iter_scans(max_buf_meas=1500)):
                    if INLOCSYNC or ALWAYS_LOG:
                        lidartime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                        data = []
                        for (_, angle, distance) in scan:
                            if distance > 0:
                                data.append((int(angle)%360, int(distance)))
                        lidar_data = {
                            'class': 'LIDAR',
                            'device': 'A1M8',
                            'time': lidartime,
                            'scan': data,
                        }
                        lidar_output.write("%s %s %s *\n" % (lidar_data['time'], lidar_data['class'], json.dumps(lidar_data)))
                        LIDAR_DATA = lidar_data
                    LIDAR_STATUS = True
                    if DONE:
                        break
        except KeyboardInterrupt:
            DONE = True
        except Exception as ex:
            mylog("LIDAR Logger Exception: %s" % ex)
            time.sleep(ERROR_DELAY)

        if lidar is not None:
            lidar.stop()
            lidar.stop_motor()
            lidar.disconnect()
        LIDAR_STATUS = False
        time.sleep(ERROR_DELAY)


def lidar_logger_wrapper(output_directory):
    """ Wrapper Around LIDAR Logger Function """
    global LIDAR_STATUS
    LIDAR_STATUS = False
    try:
        lidar_logger(output_directory)
    except Exception as ex:
        mylog("LIDAR Logger Exception: %s" % ex)
    LIDAR_STATUS = False
    mylog("LIDAR Done")

def audio_logger(output_directory):
    global DONE, AUDIO_STATUS

    # Configure
    try:
        with open("config.json", "r") as f:
            config = json.loads(f.read())
    except:
        config = {"class": "CONFIG", "audio": {"log": True}}
    config['time'] =  datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Create the output directory
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    while not INLOCSYNC:
        time.sleep(SYNC_DELAY)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    with open(os.path.join(output_directory,timestamp+"_audio.csv"), "w") as audio_output:
        audio_output.write("#v%d\n" % VERSION)
        audio_output.write("%s %s %s *\n" % (config['time'], config['class'], json.dumps(config)))
        while not DONE:
            try:
                AUDIO_STATUS = True
                timestamp = datetime.datetime.now()
                filename = timestamp.strftime("%Y%m%d%H%M")
                if os.system("./audio_collect.sh %s %s" % (output_directory, filename)) != 0:
                    AUDIO_STATUS = False
                    time.sleep(ERROR_DELAY)
                else:
                    obj = {
                        "class": "AUDIO",
                        "time": timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    }
                    for channel in ["left", "right"]:
                        capture_file = filename+"_"+channel+".wav"
                        if os.path.isfile(os.path.join(output_directory, capture_file)):
                            obj[channel] = capture_file
                    audio_output.write("%s %s %s *\n" % (obj['time'], obj['class'], json.dumps(obj)))
            except KeyboardInterrupt:
                DONE = True
            except Exception as ex:
                mylog("Audio Logger Exception: %s" % ex)
                time.sleep(ERROR_DELAY)

        AUDIO_STATUS = False

def audio_logger_wrapper(output_directory):
    """ Wrapper Around Audio Logger Function """
    global AUDIO_STATUS
    AUDIO_STATUS = False
    try:
        audio_logger(output_directory)
    except Exception as ex:
        mylog("Audio Logger Exception: %s" % ex)
    AUDIO_STATUS = False
    mylog("Audio Done")

# MAIN START
INLOCSYNC = False
DONE = False
RESTART = True
VERSION = 9
CURRENT = {}
TEMP = 0
HOLD = -1
MEMO = ""

GPS_STATUS = 0
GPS_NUM_SAT = 0
GPS_NUM_USED = 0
ACC_STATUS = False
LIDAR_STATUS = False
LIDAR_DATA = {}
AUDIO_STATUS = False

# Output Directory
try:
    OUTPUT = sys.argv[1]
except IndexError:
    OUTPUT = "/root/gps-data"

# Listen on port 2947 (gpsd) of localhost
SESSION = gps.gps("localhost", "2947")
SESSION.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

# Web Server
httpd = HTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)

Twww = threading.Thread(name="W", target=web_server, args=(httpd,))
Twww.start()

# Make sure we have a time sync
wait_for_timesync(SESSION)

mylog("Have Timestamp")

try:
    if CONFIG['gps']['log']:
        Tgps = threading.Thread(name="GPS", target=gps_logger_wrapper, args=(OUTPUT, SESSION,))
        Tgps.start()
    if CONFIG['imu']['log']:
        Timu = threading.Thread(name="IMU", target=imu_logger_wrapper, args=(OUTPUT,))
        Timu.start()
    if CONFIG['lidar']['log']:
        Tlidar = threading.Thread(name="LIDAR", target=lidar_logger_wrapper, args=(OUTPUT,))
        Tlidar.start()
    if CONFIG['audio']['log']:
        Taudio = threading.Thread(name="AUDIO", target=audio_logger_wrapper, args=(OUTPUT,))
        Taudio.start()
except Exception as ex:
    mylog("Exception: unable to start thread: %s" % ex)
    sys.exit(-1)

while not DONE:
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as t:
            TEMP = int(t.read())/1000
            mylog({"TempC": TEMP})
        time.sleep(IDLE_DELAY)
    except KeyboardInterrupt:
        DONE = True
        imu_logger.DONE = True

httpd.shutdown()
httpd.server_close()

Twww.join()
if CONFIG['gps']['log']:
    Tgps.join()
if CONFIG['imu']['log']:
    Timu.join()
if CONFIG['lidar']['log']:
    Tlidar.join()
if CONFIG['audio']['log']:
    Taudio.join()

while not RESTART:
    time.sleep(IDLE_DELAY)
