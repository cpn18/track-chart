#!/usr/bin/env python3
import sys
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pirail
import json

TIME_ADJUST = True

CROSS_RATIO = 0.75

UPSCALE = 1.0

def wav_to_json(timestamp):
    data = pirail.read_wav_file({"time": timestamp})
    Fr = data['framerate']
    Fs = 1.0 / Fr

    increment = datetime.timedelta(seconds=Fs)

    timecode = pirail.parse_time(data['time'])
    for i in range(len(data['left'])):
        obj = {
            "time": pirail.format_time(timecode),
            "class": "LPCM",
            "left": data['left'][i],
            "right": data['right'][i],
        }
        timecode += increment
        print(json.dumps(obj))

if __name__ == "__main__":
    with open(sys.argv[-1]) as f:
        for line in f:
            obj = json.loads(line)
            if obj['class'] != "LPCM":
                print(json.dumps(obj))
                continue
            wav_to_json(obj['time'])
