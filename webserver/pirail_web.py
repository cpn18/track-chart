#!/usr/bin/python3
"""
Web Server
"""

import os
import json
import re

WEBROOT = "webroot"
DATAROOT = "data"

SORTBY = "mileage"

MIME_MAP = {
    ".html": "text/html",
    ".txt": "text/plain",
    ".js": "text/javascript",
    ".json": "application/json",
    "default": "application/octet-stream",
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
    self.send_response(200)
    self.send_header("Content-type", content_type)
    self.send_header("Content-length", str(len(output)))
    self.end_headers()
    self.wfile.write(output.encode('utf-8'))

def get_file(self, groups, _qsdict):
    """
    Data Fetching API
    GET /data/[filename]
    """
    pathname = os.path.normpath(DATAROOT + "/" + groups.group('filename'))

    if not os.path.isfile(pathname):
        self.send_error(404, "File Not Found")
        return

    data = []
    with open(pathname) as j:
        for line in j:
            obj = json.loads(line)
            # Sample method to thin the data set
            if obj['class'] == "ATT":
                data.append({
                    'class': obj['class'],
                    'time': obj['time'],
                    'mileage': obj['mileage'],
                    'acc_z': obj['acc_z'],
                })

    # Sort the data
    if SORTBY is not None:
        data = sorted(data, key=lambda k: k[SORTBY], reverse=False)

    content_type = MIME_MAP[".json"]
    output = json.dumps(data, indent=4) + "\n"

    self.send_response(200)
    self.send_header("Content-type", content_type)
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
        self.send_error(404, "File Not Found")
        return

    _, extension = os.path.splitext(pathname)
    if not extension in MIME_MAP:
        extension = 'default'

    content_type = MIME_MAP[extension]
    with open(pathname) as j:
        output = j.read()

    # If we made it this far, then send output to the browser
    self.send_response(200)
    self.send_header("Content-type", content_type)
    self.send_header("Content-length", str(len(output)))
    self.end_headers()
    self.wfile.write(output.encode('utf-8'))

MATCHES = [
    # Most specific matches go first
    {
         "pattern": re.compile(r"GET /data/(?P<filename>[a-zA-Z0-9\.]+)"),
         "handler": get_file,
    },
    # Least specifc matches go last
    {
         "pattern": re.compile(r"GET /data/"),
         "handler": get_file_listing,
    },
    # This one must be last
    {
         "pattern": re.compile(r"GET (?P<pathname>.+)"),
         "handler": get_any,
    },
]
