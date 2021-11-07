"""
PiRail Web Service Modules
"""

import os
import json
import re
import sys

# This is sort of a hack, but it's better than
# copying the PiRail module here.  It's expected that
# as this evolves, more of the analysis tools become
# web-enabled.
sys.path.append("../desktop")
import pirail


from http import HTTPStatus

# Directory for web content (html, css, js, etc.)
WEBROOT = "webroot"

# Directory for data (json)
DATAROOT = "data"

# Default sort method (set to None for no sorting)
SORTBY = "mileage"

# Replace with the Python mimetypes module?
# https://docs.python.org/3/library/mimetypes.html
MIME_MAP = {
    ".html": "text/html",
    ".txt": "text/plain",
    ".js": "text/javascript",
    ".json": "application/json",
    "default": "application/octet-stream",
}

def thin_data(obj, thin=True):
    """ Sample Data Thinning """
    if not thin:
        return obj
    else:
        return {
            'class': obj['class'],
            'time': obj['time'],
            'mileage': obj['mileage'],
            'acc_z': obj['acc_z'],
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
    GET /data/[filename]
    """
    pathname = os.path.normpath(DATAROOT + "/" + groups.group('filename'))

    if not os.path.isfile(pathname):
        self.send_error(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.description)
        return

    # Parse the query string and
    # Build the Args Dictionary
    args = {}
    try:
        stream = qsdict.get("stream",["true"])[0].lower() == "true"
        thin = qsdict.get("thin",["False"])[0].lower() == "true"
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

    print("args", args)
    print("classes", classes)

    data = []
    self.send_response(HTTPStatus.OK)
    if stream:
        self.send_header("Content-type", "text/event-stream")
        self.end_headers()
    else:
        self.send_header("Content-type", "application/json")

    for line_no, obj in pirail.read(pathname, classes=classes, args=args):
        if stream:
            output = "event: pirail\ndata: %s\n\n" % json.dumps(thin_data(obj, thin=thin))
            self.wfile.write(output.encode('utf-8'))
        else:
            data.append(thin_data(obj, thin=thin))

    if not stream:
        # Sort the data
        if SORTBY is not None:
            data = sorted(data, key=lambda k: k[SORTBY], reverse=False)

        output = json.dumps(data, indent=4) + "\n"

        self.send_header("Content-length", str(len(output)))
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))

def get_any(self, groups, _qsdict):
    """
    Generic File Handler API
    GET /[path]
    """
    pathname = os.path.normpath(WEBROOT + "/" + groups.group('pathname'))

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
    with open(pathname) as j:
        output = j.read()

    # If we made it this far, then send output to the browser
    self.send_response(HTTPStatus.OK)
    self.send_header("Content-type", content_type)
    self.send_header("Content-length", str(len(output)))
    self.end_headers()
    self.wfile.write(output.encode('utf-8'))

MATCHES = [
    # Most specific matches go first
    {
         "pattern": re.compile(r"GET /data/(?P<filename>[a-zA-Z0-9_\.]+)"),
         "handler": get_file,
    },
    # Least specifc matches go last
    {
         "pattern": re.compile(r"GET /data/*"),
         "handler": get_file_listing,
    },
    # This one must be last
    {
         "pattern": re.compile(r"GET (?P<pathname>.+)"),
         "handler": get_any,
    },
]
