"""
PiRail Web Service Modules
"""

import os
import json
import re
import sys

import pirail


from http import HTTPStatus

# Directory for web content (html, css, js, etc.)
WEBROOT = "webroot"

# Directory for data (json)
DATAROOT = os.environ.get('PIRAILDATA', "data")

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

def thin_acc_z(obj, _qsdict):
    """ Sample Data Thinning """
    if obj['class'] == "ATT":
        return {
            'class': obj['class'],
            'time': obj['time'],
            'mileage': obj['mileage'],
            'acc_z': obj['acc_z'],
        }
    else:
        return obj

def thin_pitch_roll(obj, _qsdict):
    """ Sample Data Thinning """
    if obj['class'] == "ATT":
        return {
            'class': obj['class'],
            'time': obj['time'],
            'mileage': obj['mileage'],
            'pitch': obj['pitch'],
            'roll': obj['roll'],
        }
    else:
        return obj

# Dictionary of Data Transformations
DATA_XFORM = {
    'thin': thin_acc_z,
    'attitude': thin_pitch_roll,
    'default': default,
}

def get_file_listing(self, groups, _qsdict):
    """
    Data Listing API
    GET /data/
    """
    content_type = MIME_MAP['.html']
    output = "<html><body><ul>\n"
    pathname = os.path.normpath(DATAROOT)
    for root, dirnames, filenames in os.walk(pathname):
        for filename in filenames:
            output += "<li><a href=\"/data/" + \
                      filename + "\">" + filename + "</a>\n"
    output += "</ul></body></html>\n"
    self.send_response(HTTPStatus.OK)
    self.send_header("Content-type", content_type)
    self.send_header("Content-length", str(len(output)))
    self.end_headers()
    self.wfile.write(output.encode('utf-8'))

def get_file(self, groups, qsdict):
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
        else:
            pathname = os.path.normpath(os.path.join(DATAROOT, filename))
            if not os.path.isfile(pathname):
                self.send_error(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.description)
                return

        xform = qsdict.get("xform",["default"])[0].lower()
        if xform in DATA_XFORM:
            xform_function = DATA_XFORM[xform]
        else:
            xform_function = DATA_XFORM['default']

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
            args['end-time'] = float(value)

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

    for line_no, obj in pirail.read(pathname, classes=classes, args=args):
        if stream:
            output = "event: pirail\ndata: %s\n\n" % json.dumps(xform_function(obj, qsdict))
            self.wfile.write(output.encode('utf-8'))
        else:
            data.append(xform_function(obj, qsdict))

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

def get_acoustic(self, groups, qsdict):
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
        else:
            pathname = os.path.normpath(os.path.join(DATAROOT, filename))
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
        xform_function = DATA_XFORM['default']

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
    for line_no, obj in pirail.read(pathname, classes=classes, args=args):
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

def get_stats(self, groups, qsdict):
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
        else:
            pathname = os.path.normpath(os.path.join(DATAROOT, filename))
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
            args['end-time'] = float(value)

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

        value = qsdict.get("percentile",["0.95"])[0]
        percentile = float(value)

        classes = "ATT"
        xform_function = DATA_XFORM['thin']

    except ValueError as ex:
        self.send_error(HTTPStatus.BAD_REQUEST, str(ex))
        return

    data = []
    self.send_response(HTTPStatus.OK)
    self.send_header("Content-type", "application/json")

    for line_no, obj in pirail.read(pathname, classes=classes, args=args):
        data.append(xform_function(obj, qsdict))

    # Sort the data
    data = sorted(data, key=lambda k: k['acc_z'], reverse=False)

    sum_acc_z = 0
    for obj in data:
        sum_acc_z += obj['acc_z']

    result = {
        "acc_z": {
            "min": data[0],
            "max": data[-1],
            "mean": data[int(len(data)/2)],
            "avg": sum_acc_z / len(data),
            "noise_floor": data[int(len(data)*percentile)],
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
