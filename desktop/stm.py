#!/usr/bin/env python

from PIL import Image
import trackchart
import sys

try:
  tc = trackchart.new([
       (1024,768),
       20,
       "MP",
       float(sys.argv[1]),
       float(sys.argv[2]),
       None,
       0,
       "../data/known_stm.csv",
       "../data/gps_stm.csv"
       ])
except (IndexError,ValueError):
  print "Usage: %s start_mile end_mile" % sys.argv[0]
  sys.exit()

#trackchart.border(tc)
trackchart.mainline(tc)
trackchart.mileposts(tc,from_file=True)
trackchart.bridges_and_crossings(tc)
trackchart.stations(tc)
trackchart.elevation(tc)
trackchart.curvature(tc)
trackchart.accel(tc)
trackchart.townlines(tc)
trackchart.yardlimits(tc)
trackchart.controlpoints(tc)

tc['image'].save("test.png")
