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
    return sum(data) / len(data)

def avg_exclude_bounds(data):
    try:
        return avg(sorted(data)[1:-1])
    except ZeroDivisionError:
        return avg(data)


def downsample(data, function=avg, window=0.001):
    outdata = []
    x = data[0]['x']
    i = 0
    y = []
    while i < len(data):
        if data[i]['x'] > x + window:
            outdata.append({
                "x": x,
                "y": function(y)
            })
            y = [data[i]['y']]
            x += window
        else:
            y.append(data[i]['y'])
        i += 1
    return outdata


def plot_datasets(files, field):
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
                    "y": -obj[field],
                    "x": obj['mileage']
                })
            else:
                # Inbound data
                data.append({
                    "y": obj[field],
                    "x": obj['mileage']
                })

            last_mileage = obj['mileage']

        # Sort by x axis values and Downsample
        data = downsample(
            sorted(data, key=lambda k: k['x'], reverse=False),
            function=avg_exclude_bounds,
            window=0.005
        )

        # Build the arrays for PLT
        xaxis = []
        yaxis = []
        for obj in data:
            xaxis.append(obj['x'])
            yaxis.append(obj['y'])
        plots[plot].plot(xaxis,yaxis)

        # Next
        plot += 1

if __name__ == "__main__":
    plot_datasets(FILES, "roll")
    plt.show()
