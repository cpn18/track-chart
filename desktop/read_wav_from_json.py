#!/usr/bin/env python3
import sys
import matplotlib.pyplot as plt
import numpy as np
import pirail


TIME_ADJUST = True

CROSS_RATIO = 0.75

UPSCALE = 1.0

def read_wav_from_json(filename):
    Fr = 44100
    Fs = 1.0 / Fr
    tc = 0
    xl = []
    xr = []
    ts = []
    basetime = None
    for line_no, obj in pirail.read(filename, classes=['LPCM']):
        if basetime is None:
            basetime = pirail.parse_time(obj['time'])
        xl.append(obj['left'])
        xr.append(obj['right'])
        #ts.append(tc)
        ts.append((pirail.parse_time(obj['time']) - basetime).total_seconds())
        tc += Fs

        if tc > 120:
            break

    if TIME_ADJUST:
        mindiff=None
        # Look at the first 1/100th of a second
        for offset in range(int(Fr/100)):
            diffsum = 0
            # Use a 1/2 second window
            for i in range(int(Fr/2)):
                diffsum += pow(xl[i+offset] - xr[i], 2)  # Sum of Squares
            if mindiff is None or diffsum < mindiff:
                mindiff = diffsum
                minoffset = offset
        print("Offset = %d (samples)" % minoffset)

        # Create new arrays, and copy the data
        new_xl = [0] * len(xl)
        new_xr = [0] * len(xl)
        for i in range(len(xl)):
            new_xl[i] = xl[i]
            if i < minoffset:
                new_xr[i] = 0
            else:
                new_xr[i] = xr[i - minoffset]  # shift data to the right

        xl = new_xl
        xr = new_xr

    # Noise Reduction
    if CROSS_RATIO != 0:
        for i in range(len(xl)):
            xl_val = abs(xl[i])
            xr_val = abs(xr[i])
            if xl_val > xr_val:
                xl[i] -= CROSS_RATIO * xr[i]
            elif xr_val > xl_val:
                xr[i] -= CROSS_RATIO * xl[i]

    # Scale the result
    if UPSCALE != 1:
        for i in range(len(xl)):
            xl[i] *= UPSCALE
            xr[i] *= UPSCALE

    # Apply an FFT
    NFFT = 1024
    t = np.array(ts)
    t = np.arange(0.0,Fs*len(ts), Fs) 

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4, sharex=True)
    Pxx, freqs, bins, im = ax1.specgram(xl, NFFT=NFFT, Fs=Fr, noverlap=900)
    ax2.plot(t, xl)
    ax3.plot(t, xr)
    Pxx, freqs, bins, im = ax4.specgram(xr, NFFT=NFFT, Fs=Fr, noverlap=900)

    plt.title("Time Adjust = %s, Cross Ratio = %0.2f, Scaling = %0.2f" % (TIME_ADJUST, CROSS_RATIO, UPSCALE))
    plt.show()

if __name__ == "__main__":
    read_wav_from_json(sys.argv[-1])
