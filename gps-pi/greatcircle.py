#!/usr/bin/python

import math

def distance(ptlon1,ptlat1,ptlon2,ptlat2):
	ptlon1_radians = math.radians(ptlon1)
	ptlat1_radians = math.radians(ptlat1)
	ptlon2_radians = math.radians(ptlon2)
	ptlat2_radians = math.radians(ptlat2)

	distance_radians=2*math.asin(math.sqrt(math.pow((math.sin((ptlat1_radians-ptlat2_radians)/2)),2) + math.cos(ptlat1_radians)*math.cos(ptlat2_radians)*math.pow((math.sin((ptlon1_radians-ptlon2_radians)/2)),2)))
	# 6371.009 represents the mean radius of the earth
	# shortest path distance
	distance_km = 6371.009 * distance_radians
	return distance_km;

#def bearing(ptlon1,ptlat1,ptlon2,ptlat2):
#	ptlon1_radians = math.radians(ptlon1)
#	ptlat1_radians = math.radians(ptlat1)
#	ptlon2_radians = math.radians(ptlon2)
#	ptlat2_radians = math.radians(ptlat2)
#
#        bearing = math.atan2(math.cos(ptlat1_radians)*math.sin(ptlat2_radians)-math.sin(ptlat1_radians)*math.cos(ptlat2_radians)*math.cos(ptlon2_radians-ptlon1_radians), math.sin(ptlon2_radians-ptlon1_radians)*math.cos(ptlat2_radians))
#        return bearing;


def bearing(ptlon1,ptlat1,ptlon2,ptlat2):
        dLon = math.radians(ptlon2 - ptlon1)
        lat1 = math.radians(ptlat1)
        lat2 = math.radians(ptlat2)
        y = math.sin(dLon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dLon)
        return math.atan2(y,x);
