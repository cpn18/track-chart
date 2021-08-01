#!/usr/bin/env python
import sys
import json
import math
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import lidar_a1m8 as lidar_util
import pirail

def main():
    try:
        filename = sys.argv[1]
    except:
        print("USAGE: %s filename" % sys.argv[0])
        sys.exit(1)

    data = []
    for line_no,obj in pirail.read(filename, classes=['LIDAR']):
        data.append(obj)

    x_data=[]
    y_data=[]
    z_data=[]
    count = 1
    base_mileage = data[0]['mileage']
    for scan in data:
        count += 1
        if count % 10 == 0:
            for angle, distance in scan['scan']:
                distance = lidar_util.estimate_from_lidar(float(distance))
                if distance > 0.0:
                    x, y = pirail.vector_to_coordinates(angle+OFFSET, distance)
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
