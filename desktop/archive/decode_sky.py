#!/usr/bin/env python3
"""
Decode SKY data
"""
import os
import sys
import csv
import geo

def read_file(filename):
    data = []
    with open(filename, "r") as f:
        for line in csv.reader(f, delimiter=' ', quotechar="'"):
            if len(line) > 5 and line[1] =="SKY" and line[-1] == '*':
                obj = {
                    'timestamp': line[0].split('.')[0],
                    'device': line[2],
                    'time': line[3],
                    'gdop': line[4],
                    'hdop': line[5],
                    'pdop': line[6],
                    'tdop': line[7],
                    'vdop': line[8],
                    'xdop': line[9],
                    'ydop': line[10],
                    'satellites': [],
                }
                i = 11
                while i < len(line)-1:
                    s = {
                        'PRN': line[i],
                        'az': line[i+1],
                        'el': line[i+2],
                        'ss': line[i+3],
                        'used': line[i+4] == 'True',
                        'gnssid': line[i+5],
                        'svid': line[i+6],
                        'sigid': line[i+7],
                        'freqid': line[i+8],
                        'health': line[i+9],
                    }
                    obj['satellites'].append(s)
                    i += 10

                data.append(obj)

    return data

d1 = read_file(sys.argv[1])


for d in d1:
    used = 0
    for s in d['satellites']:
        if s['used']:
            used += 1
    print(d['timestamp'], used, len(d['satellites']))
