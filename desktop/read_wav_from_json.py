#!/usr/bin/env python3
"""
Plot WAV file data

Example: read_wav_from_json.py \
           --time-start "2022-10-15T12:12:00" \
           --time-end "2022-10-15T12:13:00" \
           wrr_20221015_eastbound_with_mileage_sort_by_time.json

This plots the first file pair found
"""
import sys
import matplotlib.pyplot as plt
import numpy as np
import pirail


# Try to sync left and right channels
TIME_ADJUST = True

# Noise reduction ratio
CROSS_RATIO = 0.75

# Scale factor
UPSCALE = 1.0

# FFT Size
NFFT = 1024
NOVERLAP = 900

def read_wav_from_json(filename):
    """ Read WAV Data Based on LPCM Records in JSON File """
    left_data = []
    right_data = []
    for _line_no, obj in pirail.read(filename, classes=['LPCM']):
        data = pirail.read_wav_file(obj)
        left_data = data['left']
        right_data = data['right']
        timestamps = np.array(data['ts'])
        framerate = data['framerate']
        # Only read read the first file pair returned
        break

    if TIME_ADJUST:
        mindiff=None
        # Look at the first 1/100th of a second
        for offset in range(int(framerate/100)):
            diffsum = 0
            # Use a 1/2 second window
            for i in range(int(framerate/2)):
                diffsum += pow(left_data[i+offset] - right_data[i], 2)  # Sum of Squares
            if mindiff is None or diffsum < mindiff:
                mindiff = diffsum
                minoffset = offset
        print("Offset = %d (samples)" % minoffset)

        # Create new arrays, and copy the data
        new_left_data = [0] * len(left_data)
        new_right_data = [0] * len(left_data)
        for i in range(len(left_data)):
            new_left_data[i] = left_data[i]
            if i < minoffset:
                new_right_data[i] = 0
            else:
                new_right_data[i] = right_data[i - minoffset]  # shift data to the right

        left_data = new_left_data
        right_data = new_right_data

    # Noise Reduction
    if CROSS_RATIO != 0:
        for i in range(len(left_data)):
            left_data_val = abs(left_data[i])
            right_data_val = abs(right_data[i])
            if left_data_val > right_data_val:
                left_data[i] -= CROSS_RATIO * right_data[i]
            elif right_data_val > left_data_val:
                right_data[i] -= CROSS_RATIO * left_data[i]

    # Scale the result
    if UPSCALE != 1:
        for i in range(len(left_data)):
            left_data[i] *= UPSCALE
            right_data[i] *= UPSCALE


    _fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4, sharex=True)
    _pxx, _freqs, _bins, _im = ax1.specgram(left_data, NFFT=NFFT, Fs=framerate, noverlap=NOVERLAP)
    ax2.plot(timestamps, left_data)
    ax3.plot(timestamps, right_data)
    _pxx, _freqs, _bins, _im = ax4.specgram(right_data, NFFT=NFFT, Fs=framerate, noverlap=NOVERLAP)

    plt.title("Time Adjust = %s, Cross Ratio = %0.2f, Scaling = %0.2f" % (TIME_ADJUST, CROSS_RATIO, UPSCALE))
    plt.show()

if __name__ == "__main__":
    read_wav_from_json(sys.argv[-1])
