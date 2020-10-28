#!/usr/bin/env python

from PIL import Image
import trackchart
import os
import sys

def main():
    try:
      tc = trackchart.new([
           (1024,768),
           20,
           float(sys.argv[1]),
           float(sys.argv[2]),
           "../known/wolfeboro.csv",
           sys.argv[3],
           ])
    except (IndexError,ValueError):
      print("Usage: %s start_mile end_mile" % sys.argv[0])
      sys.exit()

    trackchart.read_data(tc)

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

    filename = "images/wolfeboro_%s_%s.png" % (sys.argv[1], sys.argv[2])
    tc['image'].save(filename)
    os.system("eog %s" % filename)

if __name__ == "__main__":
    main()
