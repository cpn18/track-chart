#!/usr/bin/python

import fileinput
import greatcircle

lat4 = lat3 = lat2 = lat1 = 0
lon4 = lon3 = lon2 = lon1 = 0
count = 0

for line in fileinput.input():
  (time,lon,lat,alt,d) = line.split()
  lat4 = lat3
  lat3 = lat2
  lat2 = lat1
  lat1 = lat 
  lon4 = lon3
  lon3 = lon2
  lon2 = lon1
  lon1 = lon 
  count += 1
  if count > 3:
    b1 = bearing(lon1,lat1,lon2,lat2)
    d = distance(lon2,lat2,lon3,lat3)
    b2 = bearing(lon4,lat4,lon3,lat3)

    
