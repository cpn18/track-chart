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
                                 20, float(sys.argv[1]), float(sys.argv[2]),
                                 "../known/conway_branch.csv", sys.argv[3]])
    except (IndexError, ValueError):
        print("Usage: %s start_mile end_mile" % sys.argv[0])
        sys.exit()

    trackchart.read_data(mychart)

    #print("border")
    #trackchart.border(mychart)
    print("mainline")
    trackchart.mainline(mychart)
    print("mileposts")
    trackchart.mileposts(mychart, from_file=False)
    print("bridges")
    trackchart.bridges_and_crossings(mychart)
    print("stations")
    trackchart.stations(mychart)
    print("elevation")
    trackchart.elevation(mychart)
    print("curvature")
    #trackchart.curvature(mychart)
    print("accel")
    #trackchart.accel(mychart)
    print("lidar-gage")
    #trackchart.gage(mychart)
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


    filename = "images/conway_%s_%s.png" % (sys.argv[1], sys.argv[2])
    mychart['image'].save(filename)
    os.system("eog %s" % filename)

if __name__ == "__main__":
    main()