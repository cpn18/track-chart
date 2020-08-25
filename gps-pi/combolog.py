#!/usr/bin/python

import gps
import math
import datetime
import thread
#import the adxl345 module
import adxl345
import time
import greatcircle

lock = thread.allocate_lock()
gpstime = ""

def gps_logger():
  global inSync,gpstime
  logging = False

  # feet
  threshold = 25

  # Listen on port 2947 (gpsd) of localhost
  session = gps.gps("localhost", "2947")
  session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

  lastlon=9999
  lastlat=9999
  d = datetime.datetime.utcnow()
  lasttime=d.strftime("%Y-%m-%dT%H:%M:%S.000Z")
  x=0
  y=0
  z=9.807
  count=0
  while True:
    try:
        # GPS
    	report = session.next()
		# Wait for a 'TPV' report and display the current time
		# To see all report data, uncomment the line below
	#print report
        systime = time.time()

        if report['class'] == 'TPV':
            if hasattr(report, 'lat') and hasattr(report, 'lon') and hasattr(report, 'time'):
                gpstime = report.time
                inSync=1
		if lastlon == 9999:
			lastlon = report.lon
			lastlat = report.lat
                        lasttime = report.time
                        logging = True
                        lastsystime = systime

		d = greatcircle.distance(lastlon,lastlat,report.lon,report.lat) * 0.621371 * 5280
                if (lastsystime != systime):
                  speed = d / (systime - lastsystime)
                else:
                  speed = 0

                b = math.degrees(greatcircle.bearing(lastlon,lastlat,report.lon,report.lat))
                if b < 0:
                        b += 360.0

                if hasattr(report, 'alt'):
		  a = report.alt * 3.28084
                else:
                  a = 0

                if (count % 60 == 0 or d >= threshold) and logging == True:
                        lock.acquire()
                	print ( "%f %s G % 03.6f % 02.6f %03f %01.3f %01.3f %03.1f *" % (systime,report.time,report.lon,report.lat,a,d,speed,b))
                        lock.release()
			lastlon = report.lon
			lastlat = report.lat
                        lasttime = report.time
                        count = 0
                count += 1

    except KeyError:
		pass
    except KeyboardInterrupt:
		quit()
    except StopIteration:
		session = None
		print "GPSD has terminated"


def accel_logger():
  global inSync,gpstime
  #create ADXL345 object
  accel = adxl345.ADXL345()

  x0 = x1 = x2 = 0 
  y0 = y1 = y2 = 0
  z0 = z1 = z2 = 0
  c = 0
  lasttime=""
  while True:
    try:
      if inSync == 0:
        time.sleep(5)
        continue

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

      d = datetime.datetime.utcnow()
      now=d.strftime("%Y-%m-%dT%H:%M:%S.000Z")
      if now != lasttime:
        lasttime=now
        x1 = x1/c
        y1 = y1/c
        z1 = z1/c
        lock.acquire()
        print ("%f %s A %d % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f *" % (time.time(),gpstime,c,x0,x1,x2,y0,y1,y2,z0,z1,z2))
        lock.release()
        x2 = -10
        x0 = 10
        y2 = -10
        y0 = 10
        z2 = -10
        z0 = 10
        c = 1
    except InteruptedException:
      quit()

# MAIN START
inSync=0
print ""
print "#v2"
try:
  thread.start_new_thread(gps_logger,())
  thread.start_new_thread(accel_logger,())
except:
  print "Error: unale to start thread"
  exit

try:
  while 1:
    time.sleep(600)
except KeyboardInterrupt:
  exit
