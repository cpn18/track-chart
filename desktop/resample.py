#!/usr/bin/env python
import sys

#            2019-09-01T12:44:05.016682Z A -0.931  1.070  9.681 *

def resample(data):
    new_data = []
    last_time = data[0][0].split('.')[0]
    last_ms = float("."+(data[0][0].split('.')[1]).replace('Z',''))
    last_ms = int(last_ms*100)
    temp_data = {}
    this_line = []

    for d in data:
        this_time = d[0].split('.')[0]
        this_ms = float("."+(d[0].split('.')[1]).replace('Z',''))
        this_ms = int(this_ms*100)
        if this_time == last_time:
            if last_ms != this_ms:
                this_line = []
                last_ms = this_ms
            this_line.append((d[1], d[2], d[3]))
            temp_data[this_ms] = this_line
            #print "%d %s" % (this_ms,temp_data[this_ms])
        else:
            for i in range(0,100):
                timestamp = last_time + ".%02d0Z" % i
                try:
                    #print "%d %d %s" % (i, len(temp_data[i]), temp_data[i])
                    if len(temp_data[i]) == 0:
                        new_data.append((timestamp, 0, 0, 0))
                    else:
                        count = len(temp_data[i])
                        sumx = sumy = sumz = 0
                        for j in range(0, count):
                            sumx += temp_data[i][j][0]
                            sumy += temp_data[i][j][1]
                            sumz += temp_data[i][j][2]
                        new_data.append((timestamp, sumx/count, sumy/count, sumz/count))
                except KeyError:
                    new_data.append((timestamp, 0, 0, 0))
            this_line = []
            last_time = this_time
            temp_data = {}
    return new_data

if __name__ == "__main__":
    data = []
    with open(sys.argv[1], "r") as f:
        for line in f:
            items = line.split()
            try:
                if items[1] != "A":
                    continue
                if items[5] != "*":
                    continue
                data.append((items[0], float(items[2]),  float(items[3]),  float(items[4])))
            except IndexError:
                pass

    new_data = resample(data)

    #print new_data

    for d in new_data:
        print "%s A %f %f %f" % (d[0], d[1], d[2], d[3])
