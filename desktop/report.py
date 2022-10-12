#!/usr/bin/env python3
"""
Generate a tabular report based on acc_z data
"""
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
        acc_z_min = min(acc_z_min, obj['acc_z'])
        acc_z_max = max(acc_z_max, obj['acc_z'])
    acc_z_avg = acc_z_sum / len(data)
    return {
        'min': acc_z_min,
        'avg': acc_z_avg,
        'max': acc_z_max,
        'deltaz': acc_z_max - acc_z_min,
        'mileage': (data[0]['mileage'] + data[-1]['mileage'])/2.0,
        'lat': (data[0]['lat'] + data[-1]['lat'])/2.0,
        'lon': (data[0]['lon'] + data[-1]['lon'])/2.0,
    }

def report_by_acc_z(filename):
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

    # Output the top ten
    top_ten = sorted(processed[-LIMIT:], key=lambda k: k['mileage'], reverse=False)
    print("Mileage Latitude Longitude deltaZ")
    for obj in top_ten:
        print("%0.3f %02.6f %03.6f %f" % (
            obj['mileage'],
            obj['lat'],
            obj['lon'],
            obj['deltaz']
        ))

if __name__ == "__main__":
    report_by_acc_z("wrr_20211016_westbound.json")
