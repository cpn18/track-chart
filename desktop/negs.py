#!/usr/bin/env python
"""
Test driver for track chart module
"""

import sys
import trackchart

def main():
    """
    Main
    """
    try:
        mychart = trackchart.new([(1024, 768),
                                 20, "C", float(sys.argv[1]), float(sys.argv[2]),
                                 None, None, "../data/known_negs.csv", "../data/gps_negs.csv"])
    except (IndexError, ValueError):
        print("Usage: %s start_mile end_mile" % sys.argv[0])
        sys.exit()

    #trackchart.border(mychart)
    trackchart.mainline(mychart)
    trackchart.mileposts(mychart, from_file=True)
    trackchart.bridges_and_crossings(mychart)
    trackchart.stations(mychart)
    trackchart.elevation(mychart)
    trackchart.curvature(mychart)
    trackchart.accel(mychart)
    trackchart.townlines(mychart)
    trackchart.yardlimits(mychart)
    trackchart.controlpoints(mychart)
    trackchart.sidings(mychart)

    mychart['image'].save("test.png")

if __name__ == "__main__":
    main()
