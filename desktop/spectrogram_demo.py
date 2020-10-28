#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
import math
import sys
import json

# Fixing random state for reproducibility
np.random.seed(19680801)

x_data=[]
y_data=[]
z_data=[]
t_stamp=[]
with open(sys.argv[1], "r") as f:
    for line in f:
        if line[0] == "#":
            continue
        items = line.split()
        if items[1] == "ATT":
            obj = json.loads(" ".join(items[2:-1]))
            ax = obj['acc_x']
            ay = obj['acc_y']
            az = obj['acc_z']
            ax = obj['gyro_x']
            ay = obj['gyro_y']
            az = obj['gyro_z']
        elif items[1].startswith("A"):
            ax = float(items[2])
            ay = float(items[3])
            az = float(items[4])
            gx = float(items[5])
            gy = float(items[6])
            gz = float(items[7])
        else:
            continue
        t_stamp.append(np.datetime64(items[0].replace("Z", "")))
        x_data.append(ax)
        y_data.append(ay)
        z_data.append(az)

dt = 0.02
t = np.arange(0.0, dt*len(t_stamp), dt)
#t = np.array(t_stamp)

NFFT = 1024  # the length of the windowing segments
Fs = int(1.0 / dt)  # the sampling frequency

fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(nrows=6, sharex=True)
ax1.plot(t, x_data)
ax2.plot(t, y_data)
ax3.plot(t, z_data)
Pxx, freqs, bins, im = ax4.specgram(x_data, NFFT=NFFT, Fs=Fs, noverlap=900)
Pxx, freqs, bins, im = ax5.specgram(y_data, NFFT=NFFT, Fs=Fs, noverlap=900)
Pxx, freqs, bins, im = ax6.specgram(z_data, NFFT=NFFT, Fs=Fs, noverlap=900)
# The `specgram` method returns 4 objects. They are:
# - Pxx: the periodogram
# - freqs: the frequency vector
# - bins: the centers of the time bins
# - im: the matplotlib.image.AxesImage instance representing the data in the plot
plt.show()
