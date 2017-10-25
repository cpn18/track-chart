#!/usr/bin/env python
#from math import degrees,radians, cos, sin, asin, sqrt,atan2
"""
  Combine known and collected data
"""
import sys
import datetime
import time

import geo

#count = 0

GPS_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

def swap(obj1, obj2):
    """
      Swap two objects
    """
    return (obj2, obj1)

def get_mileage(locations, lat, lon):
    """
      Calculate a mileage for a location
    """
    mileage = -1
    close1 = -1
    distance1 = 99999
    close2 = -1
    distance2 = 99999

    # Find the two closest points
    for i in range(0, len(locations)):
        if locations[i]['mileage'] is not None:
            distance = geo.great_circle(locations[i]['latitude'],
                                        locations[i]['longitude'],
                                        lat,
                                        lon)

            if distance < distance1:
                close2 = close1
                distance2 = distance1
                close1 = i
                distance1 = distance
            elif distance < distance2:
                close2 = i
                distance2 = distance

    # Distance between the two closest points
    distance3 = geo.great_circle(locations[close1]['latitude'],
                                 locations[close1]['longitude'],
                                 locations[close2]['latitude'],
                                 locations[close2]['longitude']
                                )

    # swap points so point 1 has lower mileage
    if locations[close2]['mileage'] < locations[close1]['mileage']:
        (close1, close2) = swap(close1, close2)
        (distance1, distance2) = swap(distance1, distance2)

    #print "d1=%f, d2=%f, d3=%f" % (distance1,distance2,distance3)
    #print "point1=%s, point2=%s" % (locations[close1]['description'],
    #                                locations[close2]['description'])
    #print "point1=%f, point2=%f" % (locations[close1]['mileage'],
    #                                locations[close2]['mileage'])

    try:
        if distance1 == 0:
            #print "point1"
            mileage = locations[close1]['mileage']
        elif distance2 == 0:
            #print "point2"
            mileage = locations[close2]['mileage']
        elif distance3 < distance1 and distance2 < distance1:
            #print "after"
            mileage = (locations[close2]['mileage'] + distance2 +
                       locations[close1]['mileage'] + distance1) / 2.0
        elif distance3 < distance2 and distance1 < distance2:
            #print "before"
            mileage = (locations[close1]['mileage'] - distance1 +
                       locations[close2]['mileage'] - distance2) / 2.0
        elif distance1 < distance3 and distance2 < distance3:
            #print "between"
            mileage = locations[close1]['mileage'] + distance1 * (
                locations[close2]['mileage'] - locations[close1]['mileage']) / (
                    distance1 + distance2)
        else:
            pass
    except ZeroDivisionError:
        pass

    return mileage

#with open('known_negs.csv') as f:
#with open('known_wolfeboro.csv') as f:
def read_known(file_name):
    """
       Read the known points
    """
    data = []
    with open(file_name) as myfile:
        for line in myfile:
            if line[0] == '#':
                continue
            fields = line.strip().split(",")
            if fields[1] != "" and fields[2] != "":
                gps_object = {'type': fields[0],
                              'latitude': float(fields[1]),
                              'longitude': float(fields[2]),
                              'description': fields[-1]
                             }
                if fields[3] != "":
                    # Input has a mileage
                    gps_object['mileage'] = float(fields[3])
                else:
                    # Input does not have a mileage
                    gps_object['mileage'] = None

                data.append(gps_object)

    # Sort the data based on mileage
    data = sorted(data, key=lambda k: k['mileage'], reverse=False)

    # Calculate Mileage for anything that didn't have it
    done = True
    for i in range(0, len(data)):
        if data[i]['mileage'] is None:
            mileage = get_mileage(data, data[i]['latitude'], data[i]['longitude'])
            if mileage > 0:
                data[i]['mileage'] = mileage
                print(data[i])
                done = False

    # Abort if any output from above
    if not done:
        sys.exit(0)

    # Re-sort the data based on mileage
    data = sorted(data, key=lambda k: k['mileage'], reverse=False)
    #print data
    return data


def build_aobject(fields, gps_object, mileage):
    """
    Build an Accelerometer Reading
    """
    # Convert the numeric fields
    for i in range(2, len(fields)-1):
        fields[i] = float(fields[i])
    # Add to the temp list
    return {'type': 'A',
            'latitude': gps_object['latitude'],
            'longitude': gps_object['longitude'],
            'mileage': mileage,
            'speed': gps_object['speed'],
            'xavg': fields[4],
            'xdiff': fields[5] - fields[3],
            'yavg': fields[7],
            'ydiff': fields[8] - fields[6],
            'zavg': fields[10],
            'zdiff': fields[11] - fields[9]
           }

def build_gps_object(fields, last_gps, mileage):
    """
    Build GPS Reading
    """
    # Convert numeric fields
    for i in range(2, len(fields)-1):
        fields[i] = float(fields[i])
    unixtime = time.mktime(datetime.datetime.strptime(
        fields[0], GPS_FORMAT).timetuple())
    gps_object = {'type': 'G',
                  'latitude': fields[2],
                  'longitude': fields[3],
                  'altitude': fields[4],
                  'distance': fields[5],
                  'speed': fields[6],
                  'bearing': fields[7],
                  'mileage': mileage,
                  'unixtime': unixtime
                 }

    # If the GPS did not report speed, then calculate it
    # based on the last position and time
    if fields[6] == 0:
        try:
            distance = geo.great_circle(last_gps['latitude'],
                                        last_gps['longitude'],
                                        gps_object['latitude'],
                                        gps_object['longitude']
                                       )
            timedelta = gps_object['unixtime'] - last_gps['unixtime']
            gps_object['speed'] = 3600.0 * distance / timedelta
            gps_object['distance'] = distance
            #print("calculated speed: %s" % gps_object)
        except KeyError:
            pass

    return gps_object

def read_raw_files(known_locations, file_list):
    """
       Read raw gps and accelerometer data files
    """
    cdata = list(known_locations)
    adata = []
    for file_name in file_list:
        gps_object = {}
        adata_temp = []
        with open(file_name) as myfile:
            for line in myfile:
                if line[0] == "#":
                    continue

                fields = line.strip().split()
                length = len(fields)

                # Empty or Impartial Lines
                if length == 0 or fields[-1] != "*":
                    continue

                # If this is GPS data...
                if length > 3 and fields[1] == "G":
                    # Calculate the mileage from known locations
                    mileage = get_mileage(known_locations,
                                          float(fields[2]), float(fields[3]))

                    # Save Last location
                    last_gps = gps_object
                    gps_object = build_gps_object(fields, last_gps, mileage)

                    # Add the object, and re-sort by mileage
                    cdata.append(gps_object)
                    cdata = sorted(cdata, key=lambda k: k['mileage'], reverse=False)

                    # If we have accelerometer data...
                    if adata_temp:
                        # Calculate delta between points
                        lat_delta = (gps_object['latitude'] -
                                     last_gps['latitude']) / len(adata_temp)
                        lon_delta = (gps_object['longitude'] -
                                     last_gps['longitude']) / len(adata_temp)
                        m_delta = (gps_object['mileage'] -
                                   last_gps['mileage']) / len(adata_temp)
                        latitude = last_gps['latitude']
                        longitude = last_gps['longitude']
                        mileage = last_gps['mileage']
                        # Create and insert each reading
                        for accel in adata_temp:
                            aobject = {'type': accel['type'],
                                       'latitude': latitude,
                                       'longitude': longitude,
                                       'mileage': mileage,
                                       'speed': accel['speed'],
                                       'xavg': accel['xavg'],
                                       'xdiff': accel['xdiff'],
                                       'yavg': accel['yavg'],
                                       'ydiff': accel['ydiff'],
                                       'zavg': accel['zavg'],
                                       'zdiff': accel['zdiff']
                                      }
                            adata.append(aobject)
                            latitude += lat_delta
                            longitude += lon_delta
                            mileage += m_delta
                        # Reset the temp array
                        adata_temp = []

                # If this is accelerometer data...
                if length > 3 and fields[1] == "A":
                    adata_temp.append(build_aobject(fields, gps_object, mileage))

    # Sort the final list by mileage
    adata = sorted(adata, key=lambda k: k['mileage'], reverse=False)
    return (adata, cdata)

def generate_gps_output(cdata):
    """
    Generate Output
    """
    # Generate output
    first = True
    lat1 = 0
    lon1 = 0
    for point in cdata:
        # If GPS Data
        if point['type'] == 'G':
            # Calculate bearing and distance bewteen points
            if first:
                first = False
                bearing = 0
                distance = 0
            else:
                distance = geo.great_circle(lat1, lon1, point['latitude'], point['longitude'])
                if distance < 0.01:
                    continue
                bearing = geo.bearing(lat1, lon1, point['latitude'], point['longitude'])

            print("%s,%0.6f,%0.6f,%0.6f,%0.6f,%d,%0.2f" % (
                point['type'], point['latitude'], point['longitude'],
                point['mileage'], point['altitude'], bearing, distance))
            lat1 = point['latitude']
            lon1 = point['longitude']

def generate_accel_output(adata):
    """
    Generate Output
    """
    first = True
    last_xavg = 0
    last_yavg = 0
    last_zavg = 0
    for point in adata:
        if point['type'] == 'A':
            if first:
                first = False
            else:
                print("%s,%0.6f,%0.6f,%0.6f,%d,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f" % (
                    point['type'], point['latitude'], point['longitude'],
                    point['mileage'], point['speed'], point['xavg']-last_xavg,
                    point['yavg']-last_yavg, point['zavg']-last_zavg,
                    point['xdiff'], point['ydiff'], point['zdiff']))
            last_xavg = point['xavg']
            last_yavg = point['yavg']
            last_zavg = point['zavg']

def main():
    """
    Main rountine
    """
    # Read the known locations
    known_locations = read_known('known_negs.csv')
    #known_locations = read_known('known_wolfeboro.csv')

    # Start reading the raw data files
    #for rawfile in ['201709051108_log_negs.csv']:
    #for rawfile in ['201706052258_log_wolfeboro_a.csv']:
    (adata, cdata) = read_raw_files(known_locations,
                                     ['201710060900_log_negs.csv'])
    #                                ['201706231117_log_negs.csv',
    #                                 '201707160116_log_negs.csv',
    #                                 '201708260206_log_negs.csv',
    #                                 '201709051108_log_negs.csv'])
    generate_gps_output(cdata)
    generate_accel_output(adata)

if __name__ == "__main__":
    main()
