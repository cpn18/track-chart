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

####

METERS_TO_DEGREES = 111111.0
def meters_to_latitude(meters):
    return meters / METERS_TO_DEGREES

def latitude_to_meters(lat):
    return lat * METERS_TO_DEGREES

def meters_to_longitude(meters, lat=0):
    return meters / (METERS_TO_DEGREES * cos(radians(lat)))

def longitude_to_meters(lon, lat=0):
    return lon * (METERS_TO_DEGREES * cos(radians(lat)))

def new_position(lat, lon, distance, bearing):
    angle = radians(bearing)
    lat += meters_to_latitude(distance * cos(angle))
    lon += meters_to_longitude(distance * sin(angle), lat)
    return (lat, lon)

if __name__ == "__main__":
    # Unit Testing
    print(new_position(0,0,111111,0))
    print(new_position(0,0,111111,45))
    print(new_position(0,0,111111,90))
    print(new_position(0,0,111111,135))
    print(new_position(0,0,111111,180))
    print(new_position(0,0,111111,270))
