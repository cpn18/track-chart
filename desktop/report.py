#!/usr/bin/env python3
"""
Generate a tabular report based on acc_z data
"""
import json
import numpy
import pirail

# How many to report
LIMIT = 20

def stats(data):
    """ Calculate min/avg/max for a segment """
    acc_z_sum = 0
    acc_z_min = 9999
    acc_z_max = -9999
    for obj in data:
        acc_z_sum += obj['acc_z']
        if obj['acc_z'] < acc_z_min:
            acc_z_min = obj['acc_z']
            acc_z_min_time = obj['time']
        if obj['acc_z'] > acc_z_max:
            acc_z_max = obj['acc_z']
            acc_z_max_time = obj['time']
    acc_z_avg = acc_z_sum / len(data)
    return {
        'min': acc_z_min,
        'avg': acc_z_avg,
        'max': acc_z_max,
        'deltaz': (acc_z_max - acc_z_min) / abs(pirail.parse_time_in_seconds(acc_z_max_time) - pirail.parse_time_in_seconds(acc_z_min_time)),
        'mileage': (data[0]['mileage'] + data[-1]['mileage'])/2.0,
        'certainty': data[0]['certainty'] * data[-1]['certainty'],
        'lat': (data[0]['lat'] + data[-1]['lat'])/2.0,
        'lon': (data[0]['lon'] + data[-1]['lon'])/2.0,
    }

def report_by_acc_z(filename):
    """ Report by Z axis - bump """
    window = 0.01 # Miles
    data = []
    for _lineno, obj in pirail.read(filename, classes="ATT"):
        data.append(obj)

    # Loop over the dataset
    processed = []
    i = j = 0
    while i+j < len(data):
        i += j
        j = 1
        start_mileage = data[i]['mileage']
        while i+j < len(data) and data[i+j]['mileage'] < start_mileage + window:
            j += 1
        processed.append(stats(data[i:i+j]))

    # Sort by deltaZ
    processed = sorted(processed, key=lambda k: k['deltaz'], reverse=False)
    max_value = processed[-1]['deltaz']

    # Output the top ten
    top_ten = sorted(processed[-LIMIT:], key=lambda k: k['mileage'], reverse=False)
    with open(filename.replace(".json", "_poi.json"), "w") as poi:
        for obj in top_ten:
            poi_obj = {
                "class": "POI",
                "label": "DeltaZ",
                "mileage": obj['mileage'],
                "lat": obj['lat'],
                "lon": obj['lon'],
                "metadata": {
                    "certainty": obj['certainty'],
                    "deltaz": obj['deltaz'] / max_value,
                    "function": "report_by_acc_z",
                    "window": window,
                }
            }
            poi.write(json.dumps(poi_obj))
            poi.write("\n")

def report_by_jerk(filename):
    """ Report by "jerk", change of acceleration """
    window = 0.01 # Miles
    data = []
    for _lineno, obj in pirail.read(filename, classes="ATT"):
        data.append(obj)

    # Loop over the dataset
    for i in range(len(data)):
        if i == 0:
            data[i]['jerkz'] = 0
        else:
            data[i]['jerkz'] = (data[i]['acc_z'] - data[i-1]['acc_z']) / (pirail.parse_time_in_seconds(data[i]['time']) - pirail.parse_time_in_seconds(data[i-1]['time']))

    # Sort by jerk
    data = sorted(data, key=lambda k: k['jerkz'], reverse=False)

    max_value = data[-1]['jerkz']

    # Output the top ten
    top_ten = sorted(data[-LIMIT:], key=lambda k: k['mileage'], reverse=False)
    with open(filename.replace(".json", "_poi.json"), "w") as poi:
        for obj in top_ten:
            poi_obj = {
                "class": "POI",
                "label": "JerkZ",
                "mileage": obj['mileage'],
                "lat": obj['lat'],
                "lon": obj['lon'],
                "metadata": {
                    "certainty": obj['certainty'],
                    "jerkz": obj['jerkz'] / max_value,
                    "function": "report_by_jerk",
                    "window": window,
                }
            }
            poi.write(json.dumps(poi_obj))
            poi.write("\n")

def report_by_stddev(filename):
    """ Report by Standard Deviation """
    window = 0.01 # Miles
    data = []
    y = []
    for _lineno, obj in pirail.read(filename, classes="ATT"):
        data.append(obj)
        y.append(obj['acc_z'])

    stddev = numpy.std(y)
    mean = numpy.mean(y)

    # Loop over the dataset
    for i in range(len(data)):
        data[i]['sigma'] = abs(data[i]['acc_z'] - mean) / stddev

    # Sort by sigma
    data = sorted(data, key=lambda k: k['sigma'], reverse=False)

    max_value = data[-1]['sigma']

    # Output the top ten
    top_ten = sorted(data[-LIMIT:], key=lambda k: k['mileage'], reverse=False)
    with open(filename.replace(".json", "_poi.json"), "w") as poi:
        for obj in top_ten:
            poi_obj = {
                "class": "POI",
                "label": "Sigma",
                "mileage": obj['mileage'],
                "lat": obj['lat'],
                "lon": obj['lon'],
                "metadata": {
                    "certainty": obj['certainty'],
                    "sigma": obj['sigma'] / max_value,
                    "function": "report_by_stddev",
                    "window": window,
                }
            }
            poi.write(json.dumps(poi_obj))
            poi.write("\n")

if __name__ == "__main__":
    report_by_acc_z("wrr_20211016_westbound.json")
    report_by_jerk("wrr_20211016_westbound.json")
    report_by_stddev("wrr_20211016_westbound.json")
