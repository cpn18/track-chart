from math import degrees,radians, cos, sin, asin, sqrt,atan2

# https://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
def haversine(lon1,lat1,lon2,lat2):
  """
  Calculate the great circle distance between two points
  on the earth (specified in decimal degrees)
  """
  lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
  dlon = lon2 - lon1
  dlat = lat2 - lat1
  a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
  c = 2 * asin(sqrt(a))
  return c * 3956.27

def bearing(lat1,lon1,lat2,lon2):
  lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

  dl = lon2 - lon1

  x = sin(dl) * cos(lat2)
  y = cos(lat1) * sin(lat2) - (sin(lat1) * cos(lat2) * cos(dl))
  ret = degrees(atan2(x,y))
  if ret < 0:
      ret += 360
  return ret
 

def great_circle(lat1,lon1,lat2,lon2):
  return haversine(lon1,lat1,lon2,lat2)
