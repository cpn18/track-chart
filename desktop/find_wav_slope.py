#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
import statistics

import wave

def main(filename):
    data = []
    ts = []
    tc = 0
    with wave.open(filename, "rb") as channel:
        params = channel.getparams()
        Fs = 1.0 / params.framerate
        for _i in range(params.nframes):
            data.append(int.from_bytes(
                channel.readframes(1)[0:params.sampwidth],
                "little",
                signed=True
            ))
            ts.append(tc)
            tc += Fs

    sdev = statistics.stdev(data)
    mean = statistics.mean(data)
    maxv = max(data)
    minv = min(data)

    print("stddev", sdev)
    print("mean", mean)
    print("max", maxv)

    # Filter
    fdata = [0] * len(data)
    for i in range(len(data)):
        if abs(data[i] - mean) > 7*sdev:
            fdata[i] = data[i]
        if data[i] == maxv:
            print(ts[i], data[i])
        if data[i] == minv:
            print(ts[i], data[i])

    #window = int(params.nframes / 600) # samples
    #skip = int(window / 2)
    #print("nframes", params.nframes)
    #print("window", window)
    #print("skip", skip)

    #count = [0] * len(data)
    #for i in range(0, len(data) - window, skip):
    #    wdata = data[i:i+window]
#
#        slope = maxv / window
#        for x in range(window):
#            y = maxv - slope * x
#            if abs(abs(wdata[x]) - y) < 10:
#                count[i] += 1


    fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4, sharex=True)
    ax1.plot(ts,data)
    Pxx, freqs, bins, im = ax2.specgram(data, NFFT=1024, Fs=params.framerate, noverlap=512)
    Pxx = Pxx.T

    print (len(Pxx), len(Pxx[0]))
    maxv=0
    for i in range(len(Pxx)):
        for j in range(len(Pxx[i])):
            if Pxx[i][j] > maxv:
                maxv=Pxx[i][j]
                pxx_i = i
                v_i = j

    print(pxx_i,v_i,maxv)

    t1 = []
    d1 = []
    for i in range(len(Pxx)):
        t1.append(bins[i])
        if Pxx[i][v_i] > 200000:
            d1.append(Pxx[i][v_i])
        else:
            d1.append(0.0)


    ax3.plot(bins, Pxx)
    ax4.plot(t1, d1)
    plt.show()


if __name__ == "__main__":
    main("/home/jminer/PIRAIL/20241020/202410201332_left.wav")

