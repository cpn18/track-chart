"""
PiRail Web Service Modules

UNH Capstone 2023 Project

Matthew Cusack, Luke Knedeisen, Joshua Knauer
"""

import os
import json
import re
from http import HTTPStatus
import statistics
import numpy

import pirail

# Directory for web content (html, css, js, etc.)
WEBROOT = "webroot"

# Default sort method (set to None for no sorting)
SORTBY = "mileage"

# Replace with the Python mimetypes module?
# https://docs.python.org/3/library/mimetypes.html
MIME_MAP = {
    ".css": "text/css",
    ".html": "text/html",
    ".txt": "text/plain",
    ".js": "text/javascript",
    ".json": "application/json",
    ".ico": "image/x-icon",
    ".png": "image/png",
    "default": "application/octet-stream",
}

def default(obj, _qsdict):
    """ Do not modify data """
    return obj

def thin(data, qsdict, data_key="acc_z", window_key="mileage", window_size=0.01, noise=1):
    """ Sample Data Thinning and Window Filter """
    if isinstance(data, dict):
        # Thin Object Data
        if data_key in data:
            return {
                'class': data['class'],
                'time': data['time'],
                'mileage': data['mileage'],
                data_key: data[data_key],
            }
    elif isinstance(data, list):
        # Window Filter
        new_data = []
        data_set = []

        # Copy the Data to array
        values = []
        for obj in data:
            values.append(obj[data_key])

        start = 0
        while True:

            # Find the Window (min size has to be two)
            end = start + 2
            while end < len(data) and abs(data[end][window_key] - data[start][window_key]) < window_size:
                end += 1

            # escape clause
            if end > len(data):
                break

            # Stats
            mean = statistics.mean(values[start:end])
            stdev = statistics.stdev(values[start:end], mean)

            for i in range(start, end):
                if abs(values[i] - mean) > noise*stdev:
                    if i not in data_set:
                        new_data.append(data[i])
                        data_set.append(i)
            start += 1
        return new_data

    # Not sure what was passed to us, so return the default
    return default(data, qsdict)

def thin_acc_z(data, qsdict):
    """ Thin Data on ACC Z """
    return thin(
        data,
        qsdict,
        data_key="acc_z",
        window_key="mileage",
        window_size=float(qsdict.get("window-size", ["0.01"])[0]),
        noise=float(qsdict.get("std-dev", ["2"])[0]),
    )

def thin_pitch_roll(obj, qsdict):
    """ Sample Data Thinning """
    if isinstance(obj, dict):
        if obj['class'] == "ATT":
            return {
                'class': obj['class'],
                'time': obj['time'],
                'mileage': obj['mileage'],
                'pitch': obj['pitch'],
                'roll': obj['roll'],
            }
    elif isinstance(obj, list):
        data = []
        for item in obj:
            data.append(thin_pitch_roll(item, qsdict))
        obj = data

    return obj

def thin_acoustic(obj, _qsdict):
    """ Thins Acoustic Data """
    new_left = []
    new_right = []
    new_ts = []
    fifty_increment = []
    for i in obj['left']:
        fifty_increment.append(i)
        if len(fifty_increment) == 50:
            max_num = max(fifty_increment, key=abs)
            fifty_increment.clear()
            new_left.append(max_num)
    fifty_increment.clear()
    for i in obj['right']:
        fifty_increment.append(i)
        if len(fifty_increment) == 50:
            max_num = max(fifty_increment, key=abs)
            fifty_increment.clear()
            new_right.append(max_num)
    fifty_increment.clear()
    for i in obj['ts']:
        fifty_increment.append(i)
        if len(fifty_increment) == 50:
            new_ts.append(statistics.median(fifty_increment))
            fifty_increment.clear()
    return {
            'class': obj['class'],
            'time': obj['time'],
            'mileage': obj['mileage'],
            'left': new_left,
            'right': new_right,
            'ts': new_ts,
        }

def thin_acoustic_2(obj, _qsdict):
    """ Thins Acoustic Data """
    #std is standard deviation, edit this variable to change how graph is thinned
    std = 4
    new_left = []
    new_right = []
    left_ts = []
    right_ts = []
    left_abs = [abs(x) for x in obj['left']]
    mean_left = statistics.mean(left_abs)
    std_left = (numpy.std(left_abs) * std) + mean_left
    #print(mean_left,numpy.std(left_abs),two_std_left)
    right_abs = [abs(x) for x in obj['right']]
    mean_right = statistics.mean(right_abs)
    std_right = (numpy.std(right_abs) * std) + mean_right
    for idx, i in enumerate(obj['left']):
        if (i > std_left) or (i < -std_left):
            new_left.append(i)
            #print(idx, i)
            left_ts.append(obj['ts'][idx])
    for idx, i in enumerate(obj['right']):
        if (i > std_right) or (i < -std_right):
            new_right.append(i)
            right_ts.append(obj['ts'][idx])
    return {
            'class': obj['class'],
            'time': obj['time'],
            'mileage': obj['mileage'],
            'left': new_left,
            'right': new_right,
            'ts': left_ts,#obj['ts'],
            'left_ts': left_ts,
            'right_ts': right_ts,
        }

def thin_acoustic_3(obj, qsdict):
    """ Thins Acoustic Data """
    # Number of standard deviations to use as the noise floor
    noise = float(qsdict.get('std-dev', ["2"])[0])

    # New data arrays
    new_left = []
    new_right = []
    left_ts = []
    right_ts = []

    # Left Channel
    mean_left = statistics.mean(obj['left'])
    noise_floor_left = statistics.stdev(obj['left'], mean_left) * noise

    for idx, i in enumerate(obj['left']):
        if abs(i) > noise_floor_left:
            new_left.append(i)
            left_ts.append(obj['ts'][idx])

    # Right Channel
    mean_right = statistics.mean(obj['right'])
    noise_floor_right = statistics.stdev(obj['right'], mean_right) * noise

    for idx, i in enumerate(obj['right']):
        if abs(i) > noise_floor_right:
            new_right.append(i)
            right_ts.append(obj['ts'][idx])

    # Downsample the remaining data
    windowsize = 15

    # Left channel Data and Timestamp
    final_left = []
    final_ts_left = []
    window = []
    for i in new_left:
        window.append(i)
        if len(window) == windowsize:
            # Preserve the maximum absolute value in the window
            final_left.append(max(window, key=abs))
            window.clear()

    window.clear()
    for i in left_ts:
        window.append(i)
        if len(window) == windowsize:
            # Preserve tje median timestamp for the window
            final_ts_left.append(statistics.median(window))
            window.clear()

    # Right channel Data and Timestamp
    final_right = []
    final_ts_right = []
    window.clear()
    for i in new_right:
        window.append(i)
        if len(window) == windowsize:
            final_right.append(max(window, key=abs))
            window.clear()

    window.clear()
    for i in right_ts:
        window.append(i)
        if len(window) == windowsize:
            final_ts_right.append(statistics.median(window))
            window.clear()

    return {
            'class': obj['class'],
            'time': obj['time'],
            'mileage': obj['mileage'],
            'left': final_left,
            'left_ts': final_ts_left,
            'right': final_right,
            'right_ts': final_ts_right,
        }

# Dictionary of Data Transformations
DATA_XFORM = {
    'thin_acc_z': thin_acc_z,
    'attitude': thin_pitch_roll,
    'default': default,
    'acoustic': thin_acoustic,
    'acoustic2': thin_acoustic_2,
    'acoustic3': thin_acoustic_3,
}


def get_file_listing(self, _groups, _qsdict):
    """
    Data Listing API
    GET /data/
    """
    if self.headers['accept'] == "application/json":
        content_type = "application/json"
        array_of_files = []
        for filename in pirail.list_files(regex=r'.*json$'):
            basename = os.path.basename(filename)
            array_of_files.append(basename)
        output = json.dumps(array_of_files)
    else:
        content_type = MIME_MAP['.html']
        output = "<html><body><ul>\n"
        for filename in pirail.list_files(regex=r'.*json$'):
            basename = os.path.basename(filename)
            output += "<li><a href=\"/data/" + \
                      basename + "\">" + basename + "</a>\n"
        output += "</ul></body></html>\n"

    self.send_response(HTTPStatus.OK)
    self.send_header("Content-type", content_type)
    self.send_header("Content-length", str(len(output)))
    self.end_headers()
    self.wfile.write(output.encode('utf-8'))

def get_file(self, _groups, qsdict):
    """
    Data Fetching API
    GET pirail_data_fetch.php
    """

    # Parse the query string and
    # Build the Args Dictionary
    args = {}
    try:
        if self.headers['accept'] == "application/json":
            stream = False
        elif self.headers['accept'] == "text/event-stream":
            stream = True
        else:
            stream = qsdict.get("stream",["true"])[0].lower() == "true"

        filename = qsdict.get("file", [None])[0]
        if filename is None:
            self.send_error(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.description)
            return

        pathname = pirail.list_files(filename=filename)
        if not os.path.isfile(pathname):
            self.send_error(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.description)
            return

        xform = qsdict.get("xform",["default"])[0].lower()
        xform_function = DATA_XFORM.get(xform, DATA_XFORM['default'])

        value = qsdict.get("start-mileage",[None])[0]
        if value is not None:
            args['start-mileage'] = float(value)

        value = qsdict.get("end-mileage",[None])[0]
        if value is not None:
            args['end-mileage'] = float(value)

        value = qsdict.get("start-time",[None])[0]
        if value is not None:
            args['start-time'] = value

        value = qsdict.get("end-time",[None])[0]
        if value is not None:
            args['end-time'] = value

        value = qsdict.get("start-latitude",[None])[0]
        if value is not None:
            args['start-latitude'] = float(value)

        value = qsdict.get("end-latitude",[None])[0]
        if value is not None:
            args['end-latitude'] = float(value)

        value = qsdict.get("start-longitude",[None])[0]
        if value is not None:
            args['start-longitude'] = float(value)

        value = qsdict.get("end-longitude",[None])[0]
        if value is not None:
            args['end-longitude'] = float(value)

        classes = qsdict.get("classes", None)

    except ValueError as ex:
        self.send_error(HTTPStatus.BAD_REQUEST, str(ex))
        return

    data = []
    self.send_response(HTTPStatus.OK)
    if stream:
        self.send_header("Content-type", "text/event-stream")
        self.end_headers()
    else:
        self.send_header("Content-type", "application/json")

    for _line_no, obj in pirail.read(pathname, classes=classes, args=args):
        if stream:
            output = "event: pirail\ndata: %s\n\n" % json.dumps(xform_function(obj, qsdict))
            self.wfile.write(output.encode('utf-8'))
        else:
            data.append(obj)

    if not stream:
        # Sort the data
        if SORTBY is not None:
            data = sorted(data, key=lambda k: k[SORTBY], reverse=False)
            data = xform_function(data, qsdict)

        output = json.dumps(data, indent=4) + "\n"

        self.send_header("Content-length", str(len(output)))
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))
    else:
        output = "event: pirail\ndata: %s\n\n" % json.dumps({"done": True})
        self.wfile.write(output.encode('utf-8'))

def get_poi(self, _groups, qsdict):
    """
    Point of Interest Fetching API
    GET pirail_poi.php
    """

    # Parse the query string and
    # Build the Args Dictionary
    args = {}
    try:
        if self.headers['accept'] == "application/json":
            stream = False
        elif self.headers['accept'] == "text/event-stream":
            stream = True
        else:
            stream = qsdict.get("stream",["true"])[0].lower() == "true"

        filename = qsdict.get("file", [None])[0]
        if filename is None:
            self.send_error(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.description)
            return

        pathname = pirail.list_files(filename=filename.replace(".json", "_poi.json"))
        if not os.path.isfile(pathname):
            self.send_error(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.description)
            return

        value = qsdict.get("start-mileage",[None])[0]
        if value is not None:
            args['start-mileage'] = float(value)

        value = qsdict.get("end-mileage",[None])[0]
        if value is not None:
            args['end-mileage'] = float(value)

        value = qsdict.get("start-latitude",[None])[0]
        if value is not None:
            args['start-latitude'] = float(value)

        value = qsdict.get("end-latitude",[None])[0]
        if value is not None:
            args['end-latitude'] = float(value)

        value = qsdict.get("start-longitude",[None])[0]
        if value is not None:
            args['start-longitude'] = float(value)

        value = qsdict.get("end-longitude",[None])[0]
        if value is not None:
            args['end-longitude'] = float(value)

        classes = "POI"
    except ValueError as ex:
        self.send_error(HTTPStatus.BAD_REQUEST, str(ex))
        return

    data = []
    self.send_response(HTTPStatus.OK)
    if stream:
        self.send_header("Content-type", "text/event-stream")
        self.end_headers()
    else:
        self.send_header("Content-type", "application/json")

    for _line_no, obj in pirail.read(pathname, classes=classes, args=args):
        if stream:
            output = "event: poi\ndata: %s\n\n" % json.dumps(obj)
            self.wfile.write(output.encode('utf-8'))
        else:
            data.append(obj)

    if not stream:
        # Sort the data
        if SORTBY is not None:
            data = sorted(data, key=lambda k: k[SORTBY], reverse=False)

        output = json.dumps(data, indent=4) + "\n"

        self.send_header("Content-length", str(len(output)))
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))
    else:
        output = "event: poi\ndata: %s\n\n" % json.dumps({"done": True})
        self.wfile.write(output.encode('utf-8'))

def get_acoustic(self, _groups, qsdict):
    """
    Data Fetching API
    GET pirail_data_fetch.php
    """

    # Parse the query string and
    # Build the Args Dictionary
    args = {}
    try:
        if self.headers['accept'] == "application/json":
            stream = False
        elif self.headers['accept'] == "text/event-stream":
            stream = True
        else:
            stream = qsdict.get("stream",["true"])[0].lower() == "true"

        filename = qsdict.get("file", [None])[0]
        if filename is None:
            self.send_error(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.description)
            return

        pathname = pirail.list_files(filename=filename)
        if not os.path.isfile(pathname):
            self.send_error(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.description)
            return

        value = qsdict.get("start-mileage",[None])[0]
        if value is not None:
            args['start-mileage'] = float(value)

        value = qsdict.get("end-mileage",[None])[0]
        if value is not None:
            args['end-mileage'] = float(value)

        value = qsdict.get("start-time",[None])[0]
        if value is not None:
            args['start-time'] = value

        value = qsdict.get("end-time",[None])[0]
        if value is not None:
            args['end-time'] = value

        value = qsdict.get("start-latitude",[None])[0]
        if value is not None:
            args['start-latitude'] = float(value)

        value = qsdict.get("end-latitude",[None])[0]
        if value is not None:
            args['end-latitude'] = float(value)

        value = qsdict.get("start-longitude",[None])[0]
        if value is not None:
            args['start-longitude'] = float(value)

        value = qsdict.get("end-longitude",[None])[0]
        if value is not None:
            args['end-longitude'] = float(value)

        classes = ["LPCM", "TPV"]
        xform_function = DATA_XFORM['acoustic3']

    except ValueError as ex:
        self.send_error(HTTPStatus.BAD_REQUEST, str(ex))
        return

    data = []
    self.send_response(HTTPStatus.OK)
    if stream:
        self.send_header("Content-type", "text/event-stream")
        self.end_headers()
    else:
        self.send_header("Content-type", "application/json")

    lpcm_obj = {}
    for _line_no, obj in pirail.read(pathname, classes=classes, args=args):
        # Try to add end_mileage
        if obj["class"] == "TPV":
            lpcm_obj["end_mileage"] = obj['mileage']
            continue

        # Output the last record
        if 'left' in lpcm_obj:
            if stream:
                output = "event: pirail\ndata: %s\n\n" % json.dumps(xform_function(lpcm_obj, qsdict))
                self.wfile.write(output.encode('utf-8'))
            else:
                data.append(xform_function(lpcm_obj, qsdict))

        # Read the new record
        try:
            obj.update(pirail.read_wav_file(obj))
        except FileNotFoundError:
            obj.update({
                "framerate": -1,
                "left": [],
                "right": [],
                "ts": [],
            })
        lpcm_obj = obj

    if not stream:
        # Sort the data
        if SORTBY is not None:
            data = sorted(data, key=lambda k: k[SORTBY], reverse=False)

        output = json.dumps(data, indent=4) + "\n"

        self.send_header("Content-length", str(len(output)))
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))
    else:
        output = "event: pirail\ndata: %s\n\n" % json.dumps({"done": True})
        self.wfile.write(output.encode('utf-8'))

def get_stats(self, _groups, qsdict):
    """
    Stats Fetching API
    GET pirail_stats_fetch.php
    """

    # Parse the query string and
    # Build the Args Dictionary
    args = {}
    try:
        filename = qsdict.get("file", [None])[0]
        if filename is None:
            self.send_error(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.description)
            return

        pathname = pirail.list_files(filename=filename)
        if not os.path.isfile(pathname):
            self.send_error(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.description)
            return

        value = qsdict.get("start-mileage",[None])[0]
        if value is not None:
            args['start-mileage'] = float(value)

        value = qsdict.get("end-mileage",[None])[0]
        if value is not None:
            args['end-mileage'] = float(value)

        value = qsdict.get("start-time",[None])[0]
        if value is not None:
            args['start-time'] = value

        value = qsdict.get("end-time",[None])[0]
        if value is not None:
            args['end-time'] = value

        value = qsdict.get("start-latitude",[None])[0]
        if value is not None:
            args['start-latitude'] = float(value)

        value = qsdict.get("end-latitude",[None])[0]
        if value is not None:
            args['end-latitude'] = float(value)

        value = qsdict.get("start-longitude",[None])[0]
        if value is not None:
            args['start-longitude'] = float(value)

        value = qsdict.get("end-longitude",[None])[0]
        if value is not None:
            args['end-longitude'] = float(value)

        value = qsdict.get("std-dev",["2"])[0]
        noise = float(value)

        classes = "ATT"
        xform_function = DATA_XFORM['thin_acc_z']

    except ValueError as ex:
        self.send_error(HTTPStatus.BAD_REQUEST, str(ex))
        return

    data = []
    self.send_response(HTTPStatus.OK)
    self.send_header("Content-type", "application/json")

    for _line_no, obj in pirail.read(pathname, classes=classes, args=args):
        data.append(xform_function(obj, qsdict))

    # Sort the data
    data = sorted(data, key=lambda k: k['acc_z'], reverse=False)

    data_acc_z = []
    for obj in data:
        data_acc_z.append(obj['acc_z'])

    # Stats
    mean = statistics.mean(data_acc_z)
    stdev = statistics.stdev(data_acc_z, mean)

    result = {
        "acc_z": {
            "min": data[0],
            "max": data[-1],
            "median": data[int(len(data)/2)],
            "avg": mean,
            "stddev": stdev,
            "noise_floor": stdev*noise,
        },
    }

    output = json.dumps(result, indent=4) + "\n"

    self.send_header("Content-length", str(len(output)))
    self.end_headers()
    self.wfile.write(output.encode('utf-8'))

def get_any(self, groups, _qsdict):
    """
    Generic File Handler API
    GET /[path]
    """
    pathname = os.path.normpath(os.path.join(WEBROOT, groups.group('pathname')))

    # Hardcoded rewrite
    if os.path.isdir(pathname):
        pathname += "/index.html"

    if not os.path.isfile(pathname):
        self.send_error(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.description)
        return

    _, extension = os.path.splitext(pathname)
    if not extension in MIME_MAP:
        extension = 'default'

    content_type = MIME_MAP[extension]
    with open(pathname, "rb") as j:
        output = j.read()

    # If we made it this far, then send output to the browser
    self.send_response(HTTPStatus.OK)
    self.send_header("Content-type", content_type)
    self.send_header("Content-length", str(len(output)))
    self.end_headers()
    self.wfile.write(output)

MATCHES = [
    # Most specific matches go first
    # Fakeout PHP handler
    {
        "pattern": re.compile(r"GET /pirail_stats_fetch.php"),
        "handler": get_stats,
    },
    # Fakeout PHP handler
    {
        "pattern": re.compile(r"GET /pirail_data_fetch.php"),
        "handler": get_file,
    },
    # Fakeout PHP handler
    {
        "pattern": re.compile(r"GET /pirail_acoustic_fetch.php"),
        "handler": get_acoustic,
    },
    # Fakeout PHP handler
    {
        "pattern": re.compile(r"GET /pirail_poi.php"),
        "handler": get_poi,
    },
    # Least specifc matches go last
    {
         "pattern": re.compile(r"GET /data/*"),
         "handler": get_file_listing,
    },
    # This one must be last
    {
         "pattern": re.compile(r"GET /(?P<pathname>.*)"),
         "handler": get_any,
    },
]
