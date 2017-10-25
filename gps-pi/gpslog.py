import gps
import math

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

lastlon=9999
lastlat=9999
while True:
    try:
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
		a = report.alt * 3.28084
                if d >= 0.01:
                	print ( "%s %f %f %f %f" % (report.time,report.lat,report.lon,a,d))
			lastlon = report.lon
			lastlat = report.lat
    except KeyError:
		pass
    except KeyboardInterrupt:
		quit()
    except StopIteration:
		session = None
		print "GPSD has terminated"

