#!/usr/bin/env python3


import json
import datetime
import time

from rplidar import RPLidar, RPLidarException 

adata=[]
done=False

data_slice = [0] * 360

stop_at = time.time() + 10
while not done:
    try:
        lidar = RPLidar("/dev/lidar")
        print(lidar.get_info())
        print(lidar.get_health())
        for i, scan in enumerate(lidar.iter_scans()):
            data = []
            for _, a, d in scan:
                if d > 0:
                    data.append((round(a)%360,round(d)))
                    data_slice[round(a)%360] = round(d)
            obj = {
                'type': "LIDAR",
                'time': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                'scan': data,
            }
            #print(json.dumps(obj))
            if data_slice[90] > 0:
                #print(data_slice[89],data_slice[90], data_slice[91])
                adata.append(data_slice[90])
            if time.time() >= stop_at:
                done=True
                break
    except RPLidarException as ex:
        print(ex)
    except KeyboardInterrupt:
        print("Disconneting")
        lidar.stop()
        lidar.stop_motor()
        break

print(round((sum(adata)-max(adata)-min(adata))/(len(adata)-2)))
