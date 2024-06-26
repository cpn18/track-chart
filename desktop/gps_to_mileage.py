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
        self.points = []
        self.min_lat = 99
        self.max_lat = -99
        self.min_lon = 180
        self.max_lon = -180
        if known_points == "-":
            return

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
                    lat = float(line[2])
                    lon = float(line[3])
                    self.min_lat = min(self.min_lat, lat)
                    self.max_lat = max(self.max_lat, lat)
                    self.min_lon = min(self.min_lon, lon)
                    self.max_lon = max(self.max_lon, lon)
                    obj.update({
                        'lat': lat,
                        'lon': lon,
                    })
                except ValueError:
                    pass

                if 'survey' in obj['metadata']:
                    obj['survey'] = util.survey_to_ft(obj['metadata']['survey'])

                self.points.append(obj)

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
        for i in sorted(self.points, key=lambda k: k['mileage'], reverse=False):

            metadata = i['metadata']

            if 'lat' in i and 'lon' in i:
                latitude = i['lat']
                longitude = i['lon']
            else:
                latitude = longitude = "-"

            print("- K %s %s %0.2f %s '%s' *" % (
                latitude,
                longitude,
                i['mileage'],
                i['class'],
                json.dumps(metadata),
            ))

    def find_measurement(self, latitude, longitude, ignore=False, field='mileage'):
        """ Find Measurement from GPS Coordinates """

        # Handles the case where there is no known file
        if len(self.points) == 0:
            return (0,1)

        measurement = close1 = close2 = -1
        distance1 = distance2 = 99999
        # Find the two closest points
        for i in range(0, len(self.points)):
            # No Geo Data
            if not ('lat' in self.points[i] and 'lon' in self.points[i]):
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

        if close1 == -1 or close2 == -1:
            # Something is very wrong if we exit here
            return (0, 0)

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

        distances = [ distance1, distance2, distance3 ]
        distances.sort()
        certainty = distances[2]/(distances[0]+distances[1])

        try:
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
        except (IndexError, KeyError):
            pass

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
                mileage, certainty = self.find_mileage(point['lat'],
                                      point['lon'],
                                      ignore=True)
                if abs(mileage - point['mileage']) > 0.01:
                    retval = False
                    if update:
                        self.points[i]['mileage'] = round(mileage, 2)
                        self.points[i]['certainty'] = certainty
                    else:
                        print(point, mileage, certainty)

        return retval

    def survey_to_mileage(self, survey):
        survey_ft = util.survey_to_ft(survey)
        i = 0
        try:
            while True:
                while self.points[i]['class'] != "MP":
                    i += 1
                j = i + 1
                while self.points[j]['class'] != "MP":
                    j += 1

                survey_ft_1 = self.points[i]['survey']
                mileage_1 = self.points[i]['mileage']
                survey_ft_2 = self.points[j]['survey']
                mileage_2 = self.points[j]['mileage']
                if survey_ft_1 <= survey_ft <= survey_ft_2:
                    return mileage_1 + (mileage_2 - mileage_1) * (survey_ft - survey_ft_1) / (survey_ft_2 - survey_ft_1)
                i = j
        except IndexError:
            pass

        return None

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
    print(G.sanity_check(update=False))
    G.export()
    print(G.find_mileage(lat, lon, ignore=True))
    print(G.find_survey(lat, lon, ignore=True))
