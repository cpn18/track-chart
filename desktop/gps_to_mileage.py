#!/usr/bin/env python3
"""
GPS to Mileage and Survey Estimation
"""
import sys
import csv
import json
import geo
import util

class Gps2Miles:
    """ GPS to Mileage and Survey """

    def __init__(self, known_points):
        data = []
        with open(known_points, "r") as known_file:
            for line in csv.reader(known_file, delimiter=' ', quotechar="'"):
                #print("LINE", line)
                if line[0][0] == "#" or line[-1] != '*' or line[1] != "K":
                    continue

                obj = {
                    'type': line[1],
                    'class': line[5],
                }
                try:
                    obj.update({
                        'mileage': float(line[4]),
                    })
                except ValueError:
                    pass

                try:
                    obj.update({
                        'metadata': json.loads(line[6]),
                    })
                except ValueError:
                    obj.update({'metadata': {}})

                try:
                    obj.update({
                        'lat': float(line[2]),
                        'lon': float(line[3]),
                    })
                except ValueError:
                    pass

                if 'survey' in obj['metadata']:
                    obj['survey'] = util.survey_to_ft(obj['metadata']['survey'])

                data.append(obj)

        # Sort the list
        self.points = sorted(data, key=lambda k: k['mileage'], reverse=False)

        # Fill in missing mileage
        for i in range(len(self.points)):
            if not 'mileage' in self.points[i]:
                if 'lat' in self.points[i] and 'lon' in self.points[i]:
                    self.points[i]['mileage'], self.points[i]['certainty'] = \
                            self.find_mileage(
                                self.points[i]['lat'],
                                self.points[i]['lon'],
                                ignore=True,
                            )

        # Resort the list
        self.points = sorted(self.points, key=lambda k: k['mileage'], reverse=False)

    def get_points(self, ktype=None, kclass=None):
        """ Return Subset of Points """
        if ktype is None and kclass is None:
            return self.points

        ret=[]
        if ktype is None and kclass is not None:
            for obj in self.points:
                if obj['class'] == kclass:
                    ret.append(obj)
        elif ktype is not None and kclass is None:
            for obj in self.points:
                if obj['type'] == ktype:
                    ret.append(obj)
        else:
            for obj in self.points:
                if obj['type'] == ktype and obj['class'] == kclass:
                    ret.append(obj)
        return ret

    def dump(self):
        """ Dump All Points """
        for i in self.points:
            print(i)

    def export(self):
        """ Export Dataset """
        print("Mileage,Latitude,Longitude,Class,Description")
        for i in sorted(self.points, key=lambda k: k['mileage'], reverse=False):
            if i['class'] == "ST":
                continue

            metadata = i['metadata']
            if 'name' in metadata:
                description = metadata['name']
            else:
                description = ""

            if 'lat' in i and 'lon' in i:
                latitude = i['lat']
                longitude = i['lon']
            else:
                latitude = longitude = ""

            print("%0.2f,%s,%s,%s,\"%s\"" % (
                i['mileage'],
                latitude,
                longitude,
                i['class'],
                description
            ))

    def find_measurement(self, latitude, longitude, ignore=False, field='mileage'):
        """ Find Measurement from GPS Coordinates """
        measurement = close1 = close2 = -1
        distance1 = distance2 = 99999
        # Find the two closest points
        for i in range(0, len(self.points)):
            # No Geo Data
            if 'lat' not in self.points[i] or 'lon' not in self.points[i]:
                continue
            # No Field Data
            if not field in self.points[i] or self.points[i][field] < 0:
                continue

            if ignore and \
               latitude == self.points[i]['lat'] and \
               longitude == self.points[i]['lon']:
                continue

            distance = geo.great_circle(self.points[i]['lat'],
                                        self.points[i]['lon'],
                                        latitude,
                                        longitude)
            if distance < distance1:
                close2 = close1
                distance2 = distance1
                close1 = i
                distance1 = distance
            elif distance < distance2:
                close2 = i
                distance2 = distance

        # Distance between the two closest points
        distance3 = geo.great_circle(self.points[close1]['lat'],
                                     self.points[close1]['lon'],
                                     self.points[close2]['lat'],
                                     self.points[close2]['lon'])

        # swap points so point 1 has lower measurement
        if self.points[close2][field] < self.points[close1][field]:
            (close1, close2) = util.swap(close1, close2)
            (distance1, distance2) = util.swap(distance1, distance2)

        #print(self.points[close1])
        #print(self.points[close2])
        #print(distance1)
        #print(distance2)
        #print(distance3)

        try:
            if distance1 == 0:
                #print("point1")
                measurement = self.points[close1][field]
            elif distance2 == 0:
                #print("point2")
                measurement = self.points[close2][field]
            elif distance3 < distance1 and distance2 < distance1:
                #print("after")
                measurement = (self.points[close2][field] + distance2 +
                           self.points[close1][field] + distance1) / 2.0
            elif distance3 < distance2 and distance1 < distance2:
                #print("before")
                measurement = (self.points[close1][field] - distance1 +
                           self.points[close2][field] - distance2) / 2.0
            elif distance1 < distance3 and distance2 < distance3:
                #print("between")
                measurement = self.points[close1][field] + \
                    distance1 * (self.points[close2][field] -
                                 self.points[close1][field]) / \
                    (distance1 + distance2)
            else:
                pass
        except ZeroDivisionError:
            print("Division by Zero!")

        # Reestimate
        for close1 in range(len(self.points)):
            if not field in self.points[close1]:
                continue
            close2 = close1 + 1
            while 'lat' not in self.points[close2] or not field in self.points[close2]:
                close2 += 1
            if self.points[close1][field] <= measurement <= self.points[close2][field]:
                # First known point to here
                distance1 = geo.great_circle(
                    self.points[close1]['lat'],
                    self.points[close1]['lon'],
                    latitude,
                    longitude,
                )
                # Here to second known point
                distance2 = geo.great_circle(
                    latitude,
                    longitude,
                    self.points[close2]['lat'],
                    self.points[close2]['lon'],
                )
                # Distance between known points
                distance3 = geo.great_circle(
                    self.points[close1]['lat'],
                    self.points[close1]['lon'],
                    self.points[close2]['lat'],
                    self.points[close2]['lon'],
                )
                measurement = self.points[close1][field] + \
                    distance1 * (self.points[close2][field] -
                                 self.points[close1][field]) / \
                    (distance1 + distance2)
                break

        distances = [ distance1, distance2, distance3 ]
        distances.sort()
        certainty = distances[2]/(distances[0]+distances[1])

        return (measurement, certainty)

    def find_mileage(self, latitude, longitude, ignore=False):
        """ Find Mileage based on GPS coordinates """
        return self.find_measurement(latitude, longitude, ignore, field='mileage')

    def find_survey(self, latitude, longitude, ignore=False):
        """ Find Survey based on GPS coordinates """
        survey, certainty = self.find_measurement(latitude, longitude, ignore, field='survey')
        return (util.ft_to_survey(survey), certainty)

    def sanity_check(self, update=False):
        """  Perform a sanity check over the data set """
        retval = True
        for i in range(0, len(self.points)):
            point = self.points[i]
            if 'lat' in point and 'lon' in point and 'mileage' in point:
                mileage = self.find_mileage(point['lat'],
                                      point['lon'],
                                      ignore=True)
                if abs(mileage - point['mileage']) > 0.01:
                    retval = False
                    if update:
                        self.points[i]['mileage'] = round(mileage, 2)
            else:
                print(point)

        return retval

if __name__ == "__main__":
    try:
        filename = sys.argv[1]
        lat = float(sys.argv[2])
        lon = float(sys.argv[3])
    except (IndexError, ValueError) as ex:
        print("ERROR: %s" % ex)
        print("\nUSAGE: %s known.csv latitude longitude" % sys.argv[0])
        sys.exit(1)

    G = Gps2Miles(filename)
    #print(G.sanity_check(update=True))
    G.export()
    print(G.find_mileage(lat, lon, ignore=True))
    print(G.find_survey(lat, lon, ignore=True))
