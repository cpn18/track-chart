import matplotlib.pyplot as plt
import numpy as np
import math

# Fixing random state for reproducibility
np.random.seed(19680801)

x_data=[]
y_data=[]
z_data=[]
t_stamp=[]
with open("../data/201909011244_accel_100sec.csv", "r") as f:
    for line in f:
        if line[0] == "#":
            continue
        items = line.split()
        if items[1] != "A":
            continue
        x = float(items[2])
        y = float(items[3])
        z = float(items[4])
        t_stamp.append(np.datetime64(items[0]))
        x_data.append(x)
        y_data.append(y)
        z_data.append(z)

dt = 0.01
t = np.arange(0.0, dt*len(t_stamp), dt)

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
