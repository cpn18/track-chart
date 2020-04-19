#!/usr/bin/python

import gps
import math
import datetime
import threading
import time
import geo
import os

import adxl345_shim as accel

def gps2date(d):
    return "%s%s%s%s%s.%s" % ( d[5:7], d[8:10], d[11:13], d[14:16], d[0:4], d[17:19] )

def gps_logger():
  global inLocSync,inTimeSync,timestamp

  # miles
  threshold = 0.0

  # Listen on port 2947 (gpsd) of localhost
  session = gps.gps("localhost", "2947")
  session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

  alt = track = speed = 0.0
  while not done:
    try:
        # GPS
    	report = session.next()
	# Wait for a 'TPV' report and display the current time
	# To see all report data, uncomment the line below
	#print report

        if report['class'] == 'TPV':
            if not inTimeSync and hasattr(report, 'time'):
                command = "date --utc %s > /dev/null" %  gps2date(report.time)
                tmp_time = report.time
                timestamp = tmp_time.replace('-','').replace(':','').replace('T','')[0:12]
                output = open("/root/gps-data/%s_gps.csv" % timestamp ,"w")
                output.write("%s\n" % version)
                output.write("%s T *\n" % report.time)
                os.system(command)
                inTimeSync = True

            if hasattr(report, 'mode'):
                if report.mode == 1:
                    continue

            if (hasattr(report, 'lat') and hasattr(report, 'lon') and hasattr(report, 'time')):
                if not inLocSync:
                    inLocSync=True
		    lastreport = report
                    continue

		distance = geo.great_circle(lastreport.lat,lastreport.lon,report.lat,report.lon)

                if hasattr(report, 'speed'):
                    speed = report.speed

                if hasattr(report, 'track'):
                    # Bearing
                    track = report.track

                if hasattr(report, 'alt'):
         	    alt = report.alt

                output.write ( "%s G % 02.6f % 03.6f %03f %01.2f %0.2f %0.2f *\n" % (report.time,report.lat,report.lon,alt,distance,speed,track))
		lastreport = report
            else:
                print(report)

    except KeyError:
		pass
    except StopIteration:
		session = None
		print "GPSD has terminated"
                output.close()


def accel_logger():
  global inLocSync

  max_x = max_y = max_z = -20
  min_x = min_y = min_z = 20
  sum_x = sum_y = sum_z = 0
  c = 0

  while not inLocSync:
      time.sleep(5)

  output = open("/root/gps-data/%s_accel.csv" % timestamp,"w")
  output.write("%s\n" % version)

  next = time.time() + 1
  while not done:
    try:

      axes = accel.get_axes()

      #put the axes into variables
      x = axes['ACCx']
      y = axes['ACCy']
      z = axes['ACCz']
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
        output.write ("%s A %d % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f *\n" % (acceltime,c,min_x,x1,max_x,min_y,y1,max_y,min_z,z1,max_z))
        max_x = max_y = max_z = -20
        min_x = min_y = min_z = 20
        sum_x = sum_y = sum_z = 0
        c = 0
        next = now + 1
    except IOError:
      pass

# MAIN START
timestamp=None
inLocSync=False
inTimeSync=False
done=False
version="#v4"
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
