"""
PiRail Common Utilities
"""
import gzip
import json
import datetime
import sys

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
        filename = name of JSON files
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

    with my_open(filename) as f:
        count = 0
        for line in f:
            count += 1

            # Parse the Line
            try:
                obj = json.loads(line)
            except Exception as ex:
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

def write(filename, data, handlers=None, classes=None, args=None):
    my_open = open
    if filename.endswith(".gz"):
        my_open = gzip.open
    with my_open(filename, "wt") as f:
        for obj in data:
            f.write(json.dumps(obj)+"\n")

def parse_time(time_string):
    """
    Parse GPS time string to datetime
    """
    return datetime.datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")

def vector_to_coordinates(angle, distance):
    x = d * math.sin(math.radians(angle))
    y = d * math.cos(math.radians(angle))
    return (x, y)

if __name__ == "__main__":
    # Unit Tests
    print(parse_cmd_line_args())
