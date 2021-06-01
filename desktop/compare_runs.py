#!/usr/bin/env python

import sys
import random
import pickle

start_mile = 3
end_mile = 3.2

data = []
for i in range(1, len(sys.argv)):
    with open(sys.argv[i] + ".pickle", "rb") as f:
        data.append(pickle.load(f))

print("Mileage Run1 Run2 Run3")
for i in range(len(data)):
    for j in range(len(data[i])):
        mileage = data[i][j]['mileage']
        if mileage < start_mile:
            continue
        elif mileage > end_mile:
            break
        elif data[i][j]['class'] == 'ATT':
            value = data[i][j]['acc_z']
            noise1 = value + random.random()*0.5
            noise2 = noise1 + random.random()*0.5

            # simulated bump
            if mileage > 3.057702 and mileage < 3.057704:
                noise1 += 2
                noise2 += 5

            print("%f %f %f %f" % (mileage, abs(value), abs(20+noise1-value), abs(40+noise2-noise1)))
