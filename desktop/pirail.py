"""
PiRail Common Utilities
"""
import json
import datetime

def read(filename, handlers=None, classes=None, start_time=None, end_time=None, start_mileage=None, end_mileage=None):
    """
    Read File
        filename = name of JSON files
        (optional)
        handlers = dictionary of handler functions, indexed by class
        start/end_time = bound results by time
        start/end_mileage = bound results by mileage

    If the handler dictionary is supplied, then call the appropriate
    handler function, indexed by class.
    Otherwise, yields the result.
    """
    with open(filename) as f:
        count = 0
        for line in f:
            count += 1

            try:
                obj = json.loads(line)
            except Exception as ex:
                print("ERROR: line=%d, %s" % (count, ex))
                raise Exception

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
            if classes is not None:
                if obj['class'] not in classes:
                    continue
            if handlers is not None:
                if obj['class'] in handlers:
                    handlers[obj['class']](count, obj)
            else:
                yield (count, obj)

def parse_time(time_string):
    """
    Parse GPS time string to datetime
    """
    return datetime.datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")

def vector_to_coordinates(angle, distance):
    x = d * math.sin(math.radians(angle))
    y = d * math.cos(math.radians(angle))
    return (x, y)
