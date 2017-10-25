#!/usr/bin/python
#import the adxl345 module
import adxl345
import math
import time
import datetime

#create ADXL345 object
accel = adxl345.ADXL345()

x0 = x1 = x2 = 0 
y0 = y1 = y2 = 0
z0 = z1 = z2 = 0
c = 0
while True:
  #get axes as g
  #axes = accel.getAxes(True)

  # to get axes as ms^2 use
  axes = accel.getAxes(False)

  #put the axes into variables
  x = axes['x']
  y = axes['y']
  z = axes['z']
  x1 += x
  y1 += y
  z1 += z
  if x > x2:
    x2 = x
  if y > y2:
    y2 = y
  if z > z2:
    z2 = z
  if x < x0:
    x0 = x
  if y < y0:
    y0 = y
  if z < z0:
    z0 = z
  c += 1

  if c == 1000:
    d = datetime.datetime.utcnow()
    lasttime=d.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    x1 = x1/c
    y1 = y1/c
    z1 = z1/c
    print ("%s A % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f " % (lasttime,x0,x1,x2,y0,y1,y2,z0,z1,z2))
    x2 = -10
    x0 = 10
    y2 = -10
    y0 = 10
    z2 = -10
    z0 = 10
    c = 1
