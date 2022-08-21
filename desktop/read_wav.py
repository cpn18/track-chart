#!/usr/bin/env python3
import sys
import wave
import matplotlib.pyplot as plt
import numpy as np


TIME_ADJUST = True

CROSS_RATIO = 0.75

UPSCALE = 1.0

def read_wav(filename):
    xl = []
    xr = []
    ts = []
    with wave.open(filename, "rb") as wf:
        params = wf.getparams()
        Fr = params.framerate
        Fs = 1.0/Fr
        tc = 0
        for i in range(params.nframes):
            data = wf.readframes(1)
            value = int.from_bytes(data, "little", signed=True)
            xl.append(value)
            ts.append(tc)
            tc += Fs

    with wave.open(filename.replace("_left","_right"), "rb") as wf:
        params = wf.getparams()
        for i in range(params.nframes):
            data = wf.readframes(1)
            value = int.from_bytes(data, "little", signed=True)
            xr.append(value)

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
    read_wav(sys.argv[-1])
