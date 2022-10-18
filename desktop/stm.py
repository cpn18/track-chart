#!/usr/bin/env python3

from PIL import Image
import trackchart
import sys
import os

try:
  tc = trackchart.new([
       (1024,768),
       20,
       float(sys.argv[-3]),
       float(sys.argv[-2]),
       "../known/stm.csv",
       sys.argv[-1],
       ])
except (IndexError,ValueError):
  print("Usage: %s start_mile end_mile" % sys.argv[0])
  sys.exit()

trackchart.mainline(tc)
trackchart.mileposts(tc,from_file=True)
trackchart.bridges_and_crossings(tc)
trackchart.stations(tc)
trackchart.elevation(tc)
trackchart.curvature(tc)
trackchart.accel(tc)
#trackchart.townlines(tc)
#trackchart.yardlimits(tc)
#trackchart.controlpoints(tc)
trackchart.draw_title(tc)

filename = "images/stm_%s_%s.png" % (sys.argv[-3], sys.argv[-2])
tc['image'].save(filename)
os.system("eog %s" % filename)
