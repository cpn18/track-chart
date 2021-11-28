#!/usr/bin/env python
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
                                 "../known/northern.csv", sys.argv[-1]])
    except (IndexError, ValueError):
        print("Usage: %s start_mile end_mile file.json" % sys.argv[0])
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
        #print("elevation")
        #trackchart.elevation(mychart)
        #print("curvature")
        #trackchart.curvature(mychart)
        #print("accel")
        #trackchart.accel(mychart)
        print("plot value")
        trackchart.plot_value(mychart, field="acc_z", scale=1)
        #print("lidar-gage")
        #trackchart.gage(mychart)
        print("string chart")
        #trackchart.string_chart_by_time(mychart)


    filename = "images/northern_%s_%s.png" % (sys.argv[-3], sys.argv[-2])
    mychart['image'].save(filename)
    os.system("eog %s" % filename)

if __name__ == "__main__":
    main()
