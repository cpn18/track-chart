"""
PiRail Common Utilities
"""
import os
import gzip
import json
import datetime
import sys
import math
import wave
import requests

# Number of Satellites
GPS_THRESHOLD = 10

# Default Directory
DEFAULT_DIRECTORY = "data"

def string_to_val(string):
    """ Convert a string to a value """
    try:
        return int(string)
    except ValueError:
        pass
    try:
        return float(string)
    except ValueError:
        pass

    if string.lower() in ["true", "false"]:
        return string.lower() == "true"

    if string.lower() in ["none", "null"]:
        return None

    return string

def parse_cmd_line_args():
    """ Build a dictionary of commandline arguments """
    args = {}
    for i in range(len(sys.argv)):
        if sys.argv[i].startswith("--"):
            args[sys.argv[i][2:]] = string_to_val(sys.argv[i+1])
            i += 1
    return args

def read(filename, handlers=None, classes=None, args=None):
    """
    Read File
        filename = name of JSON files, or URL
        (optional)
        handlers = dictionary of handler functions, indexed by class
        classes = array of classes to return
        args = dictionary of arguments, if None, then use command line

    Command Line Arguments
        start/end-time = bound results by time
        start/end-mileage = bound results by mileage
        start/end-latitude = bound results by latitude
        start/end-longitude = bound results by longitude

    If the handler dictionary is supplied, then call the appropriate
    handler function, indexed by class.
    Otherwise, yields the result.
    """
    datadir = os.environ.get('PIRAILDATA', DEFAULT_DIRECTORY)

    if datadir is not None:
        filename = os.path.join(datadir, filename)

    my_open = open
    if filename.endswith(".gz"):
        my_open = gzip.open

    if args is None:
        args = parse_cmd_line_args()

    gps_threshold = args.get("gps-threshold", GPS_THRESHOLD)

    start_time = args.get("start-time", None)
    end_time = args.get("end-time", None)
    start_mileage = args.get("start-mileage", None)
    end_mileage = args.get("end-mileage", None)
    start_latitude = args.get("start-latitude", None)
    end_latitude = args.get("end-latitude", None)
    start_longitude = args.get("start-longitude", None)
    end_longitude = args.get("end-longitude", None)

    if filename.startswith("http://"):
        response = requests.get(filename, stream=True)
        input_data = response.iter_lines()
        needs_closed=False
    else:
        input_data = my_open(filename)
        needs_closed=True

    count = 0
    for line in input_data:
        count += 1

        # Convert from bytes to str
        if not isinstance(line, str):
            line = str(line.decode('utf-8'))

        # Handle event-stream
        if line.startswith('event: pirail'):
            continue

        if line.startswith('data: '):
            line = line.split(' ', 1)[1]

        # Skip Blank Lines
        if len(line) == 0:
            continue

        # Parse the Line
        try:
            obj = json.loads(line)
        except Exception as ex:
            print("Line: %s" % line)
            print("ERROR: line=%d, %s" % (count, ex))
            raise Exception from ex

        # Check Class
        if classes is not None:
            if obj['class'] not in classes:
                continue

        # Check Quality
        if 'num_used' in obj:
            if obj['num_used'] < gps_threshold:
                continue

        # Check Bounds
        if 'time' in obj:
            if start_time is not None and obj['time'] < start_time:
                continue
            if end_time is not None and obj['time'] > end_time:
                continue
        if 'mileage' in obj:
            if start_mileage is not None and obj['mileage'] < start_mileage:
                continue
            if end_mileage is not None and obj['mileage'] > end_mileage:
                continue
        if 'lat' in obj:
            if start_latitude is not None and obj['lat'] < start_latitude:
                continue
            if end_latitude is not None and obj['lat'] > end_latitude:
                continue
        if 'lon' in obj:
            if start_longitude is not None and obj['lon'] < start_longitude:
                continue
            if end_longitude is not None and obj['lon'] > end_longitude:
                continue

        # Call the handler, or yield the result
        if handlers is not None:
            if obj['class'] in handlers:
                handlers[obj['class']](count, obj)
        else:
            yield (count, obj)

    if needs_closed:
        input_data.close()

def write(filename, data):
    """
    Write JSON to a file
    """
    datadir = os.environ.get('PIRAILDATA', DEFAULT_DIRECTORY)

    if datadir is not None:
        filename = os.path.join(datadir, filename)

    my_open = open
    if filename.endswith(".gz"):
        my_open = gzip.open
    with my_open(filename, "wt") as output_file:
        for obj in data:
            output_file.write(json.dumps(obj)+"\n")

def parse_time(time_string):
    """
    Parse GPS time string to datetime
    """
    return datetime.datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")

def parse_time_in_seconds(time_string):
    """
    Parse GPS time string to seconds
    """
    return float((parse_time(time_string) - datetime.datetime.fromtimestamp(0)).total_seconds())

def format_time(time_value):
    """
    Format GPS time string from datetime
    """
    return time_value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def vector_to_coordinates(angle, distance):
    """
    Convert vector to 2D coordinates
    """
    x_coord = distance * math.sin(math.radians(angle))
    y_coord = distance * math.cos(math.radians(angle))
    return (x_coord, y_coord)

def avg_3_of_5(data):
    """
    Average of five data points, discard the high and low points
    """
    if len(data) == 0:
        retval = 0
    if len(data) < 5:
        retval = sum(data) / len(data)
    else:
        retval = (sum(data) - min(data) - max(data)) / (len(data) - 2)
    return retval

def read_wav_file(obj):
    """
    Read a WAV Files, Return a JSON Object
    """
    datadir = os.environ.get('PIRAILDATA', DEFAULT_DIRECTORY)

    timestamp = obj['time'].split('.')[0].replace('-','').replace('T','').replace(':','')[0:12]
    if datadir is not None:
        timestamp = os.path.join(datadir, timestamp)

    result = {
        "time": obj['time'],
        "framerate": 0,
        "left": [],
        "right": [],
        "ts": [],
    }

    with wave.open(timestamp + "_left.wav", "rb") as left_channel:
        with wave.open(timestamp + "_right.wav", "rb") as right_channel:
            xl = []
            xr = []
            ts = []
            tc = 0
            params = left_channel.getparams()
            params = right_channel.getparams()
            result['framerate'] = params.framerate
            Fs = 1.0 / result['framerate']
            for _i in range(params.nframes):
                xl.append(int.from_bytes(left_channel.readframes(1), "little", signed=True))
                xr.append(int.from_bytes(right_channel.readframes(1), "little", signed=True))
                ts.append(tc)
                tc += Fs
            result['left'] = xl
            result['right'] = xr
            result['ts'] = ts
    return result

if __name__ == "__main__":
    # Unit Tests
    print(parse_cmd_line_args())
