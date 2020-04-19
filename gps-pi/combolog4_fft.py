#!/usr/bin/python

import gps
import math
import datetime
import threading
#import the adxl345 module
import adxl345
import time
import greatcircle
import numpy as np
import scipy.fftpack

lock = threading.Lock()
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
                	print ( "%f %s G % 02.6f % 03.6f %03f %01.3f %01.3f %03.1f *" % (systime,report.time,report.lat,report.lon,a,d,speed,b))
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

def fft(xa,xv,N,T):
  yf = scipy.fftpack.fft(np.array(xv))
  py = 2.0/N * np.abs(yf[:N//2])
  xf = np.linspace(0.0,1.0/(2.0*T),N/2)
  a  = np.argmax(py)
  return (xf[a],py[a])

def accel_logger():
  global inSync,gpstime
  #create ADXL345 object
  accel = adxl345.ADXL345()

  xv = []
  yv = []
  zv = []

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
      x = axes['ACCx']
      xv.append(x)
      y = axes['ACCy']
      yv.append(y)
      z = axes['ACCz']
      zv.append(z)
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
        if c > 1:
          N = c
          T = 1.0 / N
          ls = np.linspace(0.0,1.0,N)
          (ax1,ay1) = fft(ls,xv,N,T)
          (ax2,ay2) = fft(ls,yv,N,T)
          (ax3,ay3) = fft(ls,zv,N,T)
          lock.acquire()
          print "%f %s R %d %f %f %f %f %f %f *" % (time.time(),gpstime,c,ax1,ay1,ax2,ay2,ax3,ay3)
          lock.release()
        x1 = x1/c
        y1 = y1/c
        z1 = z1/c
        lock.acquire()
        #print ("%f %s A %d % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f % 02.3f *" % (time.time(),gpstime,c,x0,x1,x2,y0,y1,y2,z0,z1,z2))
        lock.release()
        x2 = -10
        x0 = 10
        y2 = -10
        y0 = 10
        z2 = -10
        z0 = 10
        c = 0
        xv = []
    except KeyboardInterrupt:
      quit()

# MAIN START
inSync=0
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

t1.join()
t2.join()
