"""
PiRail Common Utilities
"""
import gzip
import json
import datetime
import sys
import math
import requests

# Number of Satellites
GPS_THRESHOLD = 10

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
    my_open = open
    if filename.endswith(".gz"):
        my_open = gzip.open

    if args is None:
        args = parse_cmd_line_args()

    start_time = args.get("start-time", None)
    end_time = args.get("end-time", None)
    start_mileage = args.get("start-mileage", None)
    end_mileage = args.get("end-mileage", None)
    start_latitude = args.get("start-latitude", None)
    end_latitude = args.get("end-latitude", None)
    start_longitude = args.get("start-longitude", None)
    end_longitude = args.get("end-longitude", None)

    if filename.startswith("http://"):
        r = requests.get(filename, stream=True)
        f = r.iter_lines()
        needs_closed=False
    else:
        f = my_open(filename)
        needs_closed=True

    count = 0
    for line in f:
        count += 1

        # Convert from bytes to str
        if not isinstance(line, str):
            line = str(line.decode('utf-8'))

        # Handle event-stream
        if line.startswith('event: pirail'):
            continue
        elif line.startswith('data: '):
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
            raise Exception

        # Check Class
        if classes is not None:
            if obj['class'] not in classes:
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
        f.close()

def write(filename, data):
    """
    Write JSON to a file
    """
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

def vector_to_coordinates(angle, distance):
    """
    Convert vector to 2D coordinates
    """
    x_coord = distance * math.sin(math.radians(angle))
    y_coord = distance * math.cos(math.radians(angle))
    return (x_coord, y_coord)

if __name__ == "__main__":
    # Unit Tests
    print(parse_cmd_line_args())
