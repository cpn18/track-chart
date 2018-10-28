#!/usr/bin/python

import gps
import math
import datetime
import threading
#import the adxl345 module
import adxl345
import time
import geo
import os

lock = threading.Lock()

def gps2date(d):
    return "%s%s%s%s%s.%s" % ( d[5:7], d[8:10], d[11:13], d[14:16], d[0:4], d[17:19] )

def gps_logger():
  global inLocSync,inTimeSync

  # miles
  threshold = 0.0

  # Listen on port 2947 (gpsd) of localhost
  session = gps.gps("localhost", "2947")
  session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

  count=0
  alt = track = speed = 0.0
  while not done:
    try:
        # GPS
    	report = session.next()
	# Wait for a 'TPV' report and display the current time
	# To see all report data, uncomment the line below
	#print report

        if report['class'] == 'TPV':
            if hasattr(report, 'time'):
                if not inTimeSync:
                    lock.acquire()
                    print("%s T *" % report.time)
                    lock.release()
                    command = "date %s > /dev/null" % gps2date(report.time)
                    os.system(command)
                    inTimeSync = True

            if (hasattr(report, 'lat') and hasattr(report, 'lon') and hasattr(report, 'time')):
                if not inLocSync:
                    inLocSync=True
		    lastreport = report

		distance = geo.great_circle(lastreport.lat,lastreport.lon,report.lat,report.lon)

                if hasattr(report, 'speed'):
                    speed = report.speed

                if hasattr(report, 'track'):
                    # Bearing
                    track = report.track

                if hasattr(report, 'alt'):
         	    alt = report.alt

                if (count % 60 == 0 or distance >= threshold) and inLocSync == True:
                        lock.acquire()
                	print ( "%s G % 02.6f % 03.6f %03f %01.2f %0.2f %0.2f *" % (report.time,report.lat,report.lon,alt,distance,speed,track))
                        lock.release()
			lastreport = report
                        count = 0
                count += 1
            else:
                print(report)

    except KeyError:
		pass
    except StopIteration:
		session = None
		print "GPSD has terminated"



def accel_logger():
  global inLocSync
  #create ADXL345 object
  accel = adxl345.ADXL345()

  max_x = max_y = max_z = -20
  min_x = min_y = min_z = 20
  sum_x = sum_y = sum_z = 0
  c = 0

  while not inLocSync:
      time.sleep(5)

  next = time.time() + 1
  while not done:
    try:

      #get axes as g
      #axes = accel.getAxes(True)

      # to get axes as ms^2 use
      axes = accel.getAxes(False)

      #put the axes into variables
      x = axes['x']
      y = axes['y']
      z = axes['z']
      sum_x += x
      sum_y += y
      sum_z += z
      if x > max_x:
        max_x = x
      if y > max_y:
        max_y = y
      if z > max_z:
        max_z = z
      if x < min_x:
        min_x = x
      if y < min_y:
        min_y = y
      if z < min_z:
        min_z = z
      c += 1

      now=time.time()
      if now > next and c != 0:
        acceltime = time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        x1 = sum_x/c
        y1 = sum_y/c
        z1 = sum_z/c
        lock.acquire()
        print ("%s A %d % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f *" % (acceltime,c,min_x,x1,max_x,min_y,y1,max_y,min_z,z1,max_z))
        lock.release()
        max_x = max_y = max_z = -20
        min_x = min_y = min_z = 20
        sum_x = sum_y = sum_z = 0
        c = 0
        next = now + 1
    except IOError:
      pass

# MAIN START
inLocSync=False
inTimeSync=False
done=False
print ""
print "#v4"
try:
  t1 = threading.Thread(target=gps_logger, args=())
  t1.start()
  t2 = threading.Thread(target=accel_logger, args=())
  t2.start()
except:
  print "Error: unable to start thread"
  exit

while not done:
    try:
        time.sleep(60)
    except KeyboardInterrupt:
        done = True

t1.join()
t2.join()
