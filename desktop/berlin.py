#!/usr/bin/env python3

from PIL import Image
import trackchart
import os
import sys

def main():
    try:
      tc = trackchart.new([
           (1024,768),
           20,
           float(sys.argv[-3]),
           float(sys.argv[-2]),
           "../known/berlin.csv",
           sys.argv[-1],
           ])
    except (IndexError,ValueError):
      print("Usage: %s start_mile end_mile data_file" % sys.argv[0])
      sys.exit()

    trackchart.mainline(tc)
    trackchart.mileposts(tc,from_file=True)
    trackchart.bridges_and_crossings(tc)
    trackchart.stations(tc)
    #trackchart.elevation(tc)
    #trackchart.curvature(tc)
    trackchart.accel(tc)
    trackchart.townlines(tc)
    trackchart.yardlimits(tc)
    trackchart.controlpoints(tc)
    trackchart.sidings(tc)
    trackchart.draw_title(tc)

    filename = "images/berlin_%s_%s.png" % (sys.argv[-3], sys.argv[-2])
    tc['image'].save(filename)
    os.system("eog %s" % filename)

if __name__ == "__main__":
    main()
