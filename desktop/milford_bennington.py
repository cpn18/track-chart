#!/usr/bin/env python3
"""
Test driver for track chart module
"""

import sys
import os
import trackchart

def main():
    """
    Main
    """
    try:
        mychart = trackchart.new([(1024, 768),
                                 20, float(sys.argv[-3]), float(sys.argv[-2]),
                                 "../known/mb.csv", sys.argv[-1]])
    except (IndexError, ValueError):
        print("Usage: %s start_mile end_mile" % sys.argv[0])
        sys.exit()

    data_file = sys.argv[-1] != "-"

    #print("border")
    #trackchart.border(mychart)
    print("mainline")
    trackchart.mainline(mychart)
    print("mileposts")
    trackchart.mileposts(mychart, from_file=True)
    print("bridges")
    trackchart.bridges_and_crossings(mychart)
    print("stations")
    trackchart.stations(mychart)
    print("townlines")
    trackchart.townlines(mychart)
    print("yardlimits")
    trackchart.yardlimits(mychart)
    print("controlpoints")
    trackchart.controlpoints(mychart)
    print("sidings")
    trackchart.sidings(mychart)
    print("title")
    trackchart.draw_title(mychart)

    if data_file:
        print("elevation")
        trackchart.elevation(mychart)
        print("curvature")
        trackchart.curvature(mychart)
        print("accel")
        trackchart.accel(mychart)
        print("lidar-gauge")
        trackchart.draw_gauge(mychart)

    filename = "images/mb%s_%s.png" % (sys.argv[-3], sys.argv[-2])
    mychart['image'].save(filename)
    os.system("eog %s" % filename)

if __name__ == "__main__":
    main()
