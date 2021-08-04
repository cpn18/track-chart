#!/usr/bin/env python3
import wave
import matplotlib.pyplot as plt
import numpy as np

SCALE=0.5
UPSCALE=2.0

def read_wav(filename):
    x = []
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
            x.append(value)
            ts.append(tc)
            tc += Fs

    with wave.open(filename.replace("_left","_right"), "rb") as wf:
        params = wf.getparams()
        for i in range(params.nframes):
            data = wf.readframes(1)
            value = int.from_bytes(data, "little", signed=True)
            xr.append(value)

    for i in range(len(x)):
        nx = UPSCALE*(x[i] - SCALE*xr[i])
        xr[i] = UPSCALE*(xr[i] - SCALE*x[i])
        x[i] = nx

    NFFT = 1024
    t = np.array(ts)
    t = np.arange(0.0,Fs*len(ts), Fs) 

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4, sharex=True)
    ax1.plot(t, x)
    ax2.plot(t, xr)
    Pxx, freqs, bins, im = ax3.specgram(x, NFFT=NFFT, Fs=Fr, noverlap=900)
    Pxx, freqs, bins, im = ax4.specgram(xr, NFFT=NFFT, Fs=Fr, noverlap=900)
    plt.show()

if __name__ == "__main__":
    read_wav(sys.argv[-1])
