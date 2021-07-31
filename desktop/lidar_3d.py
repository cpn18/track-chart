#!/usr/bin/env python
import sys
import json
import math
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import pirail

OFFSET = 0
RANGE = 360

def read_file(filename):
    data = []
    for line_no,obj in pirail.read(filename, classes=['LIDAR']):
        data.append(obj)
    return data

def radial_to_xy(angle, distance):
    a = round(angle+OFFSET) % RANGE
    d = float(distance)
    x = d * math.sin(math.radians(a))
    y = d * math.cos(math.radians(a))
    return (x, y)


def main():
    try:
        filename = sys.argv[1]
    except:
        print("USAGE: %s filename" % sys.argv[0])
        sys.exit(1)

    x_data=[]
    y_data=[]
    z_data=[]
    count = 1
    data = read_file(filename)
    base_mileage = data[0]['mileage']
    for scan in data:
        count += 1
        scan_data = scan['scan']
        if count % 10 == 0:
            for angle, distance in scan_data:
                if distance > 0.0:
                    x, y = radial_to_xy(angle, distance)
                    x_data.append(x)
                    y_data.append(y)
                    z_data.append(scan['mileage'] - base_mileage)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(x_data, z_data, y_data, s=1, c='black', marker='o')

    ax.set_xlabel('X Label')
    ax.set_ylabel('Z Label')
    ax.set_zlabel('Y Label')

    plt.show()

if __name__ == "__main__":
    main()
