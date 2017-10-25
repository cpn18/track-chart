#!/usr/bin/python

import gps
import math

logging = True

threshold = 0.01

# Listen on port 2947 (gpsd) of localhost
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

def distance(longitude1,latitude1,longitude2,latitude2):
	ptlon1 = longitude1
	ptlat1 = latitude1
	ptlon2 = longitude2
	ptlat2 = latitude2

	ptlon1_radians = math.radians(ptlon1)
	ptlat1_radians = math.radians(ptlat1)
	ptlon2_radians = math.radians(ptlon2)
	ptlat2_radians = math.radians(ptlat2)

	distance_radians=2*math.asin(math.sqrt(math.pow((math.sin((ptlat1_radians-ptlat2_radians)/2)),2) + math.cos(ptlat1_radians)*math.cos(ptlat2_radians)*math.pow((math.sin((ptlon1_radians-ptlon2_radians)/2)),2)))
	# 6371.009 represents the mean radius of the earth
	# shortest path distance
	distance_km = 6371.009 * distance_radians
	return distance_km;

def bearing(longitude1,latitude1,longitude2,latitude2):
        return math.atan2(math.cos(latitude1)*math.sin(latitude2)-math.sin(latitude1)*math.cos(latitude2)*math.cos(longitude2-longitude1), math.sin(longitude2-longitude1)*math.cos(latitude2));


lastlon=9999
lastlat=9999
while True:
    try:
        # GPS
    	report = session.next()
		# Wait for a 'TPV' report and display the current time
		# To see all report data, uncomment the line below
	#print report

        if report['class'] == 'TPV':
            if hasattr(report, 'lat') and hasattr(report, 'lon'):
		if lastlon == 9999:
			lastlon = report.lon
			lastlat = report.lat

		d = distance(lastlon,lastlat,report.lon,report.lat) * 0.621371
                b = bearing(lastlon,lastlat,report.lon,report.lat) * 57.2958
                if b < 0:
                        b += 360.0

		a = report.alt * 3.28084

                if (d >= threshold) and logging == True:
                	print ( "%s % 03.6f % 02.6f %03f %01.3f %03.1f" % (report.time,report.lon,report.lat,a,d,b))
			lastlon = report.lon
			lastlat = report.lat
    except KeyError:
		pass
    except KeyboardInterrupt:
		quit()
    except StopIteration:
		session = None
		print "GPSD has terminated"
