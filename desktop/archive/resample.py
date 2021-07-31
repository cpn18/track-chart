#!/usr/bin/env python
import sys
import json

#            2019-09-01T12:44:05.016682Z A -0.931  1.070  9.681 *

def resample(data,bins=100):
    new_data = []
    last_time = data[0][0].split('.')[0]
    last_ms = float("."+(data[0][0].split('.')[1]).replace('Z',''))
    last_ms = int(last_ms*bins)
    temp_data = {}
    this_line = []

    for d in data:
        this_time = d[0].split('.')[0]
        this_ms = float("."+(d[0].split('.')[1]).replace('Z',''))
        this_ms = int(this_ms*bins)
        if this_time == last_time:
            if last_ms != this_ms:
                this_line = []
                last_ms = this_ms
            this_line.append((d[1], d[2], d[3], d[4], d[5], d[6]))
            temp_data[this_ms] = this_line
            #print "%d %s" % (this_ms,temp_data[this_ms])
        else:
            for i in range(0,bins):
                timestamp = last_time + ".%02d0Z" % (i*100.0/bins)
                try:
                    #print "%d %d %s" % (i, len(temp_data[i]), temp_data[i])
                    if len(temp_data[i]) == 0:
                        new_data.append((timestamp, 0, 0, 0, 0, 0, 0))
                    else:
                        count = len(temp_data[i])
                        sumx = sumy = sumz = 0
                        sumgx = sumgy = sumgz = 0
                        for j in range(0, count):
                            sumx += temp_data[i][j][0]
                            sumy += temp_data[i][j][1]
                            sumz += temp_data[i][j][2]
                            sumgx += temp_data[i][j][3]
                            sumgy += temp_data[i][j][4]
                            sumgz += temp_data[i][j][5]
                        new_data.append((timestamp, sumx/count, sumy/count, sumz/count, sumgx/count, sumgy/count, sumgz/count))
                except KeyError:
                    new_data.append((timestamp, 0, 0, 0, 0, 0, 0))
            this_line = []
            last_time = this_time
            temp_data = {}
    return new_data

if __name__ == "__main__":
    bins = 50
    data = []
    with open(sys.argv[1], "r") as f:
        for line in f:
            items = line.split()
            if items[-1] != "*":
                continue
            try:
                if items[1] == "A":
                    data.append((items[0], float(items[2]),  float(items[3]),  float(items[4]), float(items[5]), float(items[6]), float(items[7])))
                elif items[1] == "ATT":
                    obj = json.loads(" ".join(items[2:-1]))
                    data.append((items[0],
                        obj['acc_x'],
                        obj['acc_y'],
                        obj['acc_z'],
                        obj['gyro_x'],
                        obj['gyro_y'],
                        obj['gyro_z'],
                    ))
            except IndexError:
                pass

    new_data = resample(data,bins=bins)

    #print new_data

    for d in new_data:
        print("%s A%d %f %f %f %f %f %f" % (d[0], bins, d[1], d[2], d[3], d[4], d[5], d[6]))
