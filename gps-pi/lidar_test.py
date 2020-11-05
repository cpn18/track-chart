#!/usr/bin/env python3


import json
import datetime

from rplidar import RPLidar, RPLidarException 

while True:
    try:
        lidar = RPLidar("/dev/lidar")
        print(lidar.get_info())
        print(lidar.get_health())
        for i, scan in enumerate(lidar.iter_scans()):
            data = []
            for _, a, d in scan:
                if d > 0:
                    data.append((int(a)%360,int(d)))
            obj = {
                'type': "LIDAR",
                'time': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                'scan': data,
            }
            print(json.dumps(obj))
    except RPLidarException as ex:
        print(ex)
    except KeyboardInterrupt:
        print("Disconneting")
        lidar.stop()
        lidar.stop_motor()
        break
