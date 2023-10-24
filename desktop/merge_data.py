#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
import pirail

FILES = [
        "/home/jminer/PIRAIL/20210606/stm_20210606_with_mileage_sort_by_time.json",
        "/home/jminer/PIRAIL/20211017/stm_20211017_with_mileage_sort_by_time.json",
        #"/home/jminer/PIRAIL/20220902/stm_20220902_with_mileage_sort_by_time.json"
        ]

def avg(data):
    """ Average of the Dataset """
    return sum(data) / len(data)

def avg_exclude_bounds(data):
    """ Average after discarding the lowest and highest values """
    try:
        return avg(sorted(data)[1:-1])
    except ZeroDivisionError:
        return avg(data)

def max_magnitude(data):
    """ Returns the maximum magnitude of the dataset """
    value = 0
    for item in data:
        if abs(item) > abs(value):
            value = item
    return value

def delta(data):
    """ Returns the difference between high and low """
    return max(data) - min(data)

def downsample(data, function=avg, window=0.01, stride=0.5):
    """
    Downsample the Data.

    Function is any function takes an array of numbers, and returns one
    Window is in miles... 0.01 is 52ft
    Stride is a fraction of the Window, so .5 is half the window
    """
    outdata = []

    index_start = 0
    while index_start < len(data):
        window_start = data[index_start]['x']
        window_end = window_start + window
        next_stride = window_start + (window * stride)

        # Slide across the window, build array of values
        index = index_start
        y = []
        while index < len(data) and data[index]['x'] < window_end:
            y.append(data[index]['y'])
            index += 1

        # Output one value
        outdata.append({
            "x": (window_start + window_end) / 2.0,
            "y": function(y)
        })

        # Advance the window by one stride
        while index_start < len(data) and data[index_start]['x'] < next_stride:
            index_start += 1

    return outdata

def build_axis(data):
    """ Convert x/y object into two arrays """
    xaxis = []
    yaxis = []
    for obj in data:
        xaxis.append(obj['x'])
        yaxis.append(obj['y'])
    return xaxis, yaxis

def plot_datasets(files, field, outbound=1, inbound=-1):
    fig, plots = plt.subplots(nrows=len(files), sharex=True)

    plot = 0
    for filename in files:
        data = []
        last_mileage = None
        for line_no,obj in pirail.read(filename, classes=['ATT']):

            # Sanity Check
            if not 0 <= obj['mileage'] <= 2:
                continue

            if last_mileage is None:
                last_mileage = obj['mileage']

            if obj['mileage'] > last_mileage:
                # Outbound data
                data.append({
                    "y": outbound * obj[field],
                    "x": obj['mileage']
                })
            else:
                # Inbound data
                data.append({
                    "y": inbound * obj[field],
                    "x": obj['mileage']
                })

            last_mileage = obj['mileage']

        data = sorted(data, key=lambda k: k['x'], reverse=False)

        # Sort by x axis values and Downsample
        downdata = downsample(
            data,
            function=delta,
            window=0.005,
            stride=0.5,
        )

        # Build the arrays for PLT
        xaxis1, yaxis1 = build_axis(data)
        xaxis2, yaxis2 = build_axis(downdata)
        plots[plot].plot(xaxis1,yaxis1,xaxis2,yaxis2)
        plot += 1


if __name__ == "__main__":
    plot_datasets(FILES, "roll")
    plt.show()
