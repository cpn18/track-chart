#!/usr/bin/env python3
import geo
import util
import csv
import json

class Gps2Miles:

    def __init__(self, known_points):
        data = []
        with open(known_points, "r") as f:
            for line in csv.reader(f, delimiter=' ', quotechar="'"):
                print("LINE", line)
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
                except ValueError as ex:
                    obj.update({
                        'mileage': -1,
                    })

                try:
                    obj.update({
                        'metadata': json.loads(line[6]),
                    })
                except ValueError as ex:
                    obj.update({'metadata': {}})

                try:
                    obj.update({
                        'lat': float(line[2]),
                        'lon': float(line[3]),
                    })
                except:
                    pass

                data.append(obj)

        self.points = sorted(data, key=lambda k: k['mileage'], reverse=False)
        for i in range(len(self.points)):
            if self.points[i]['mileage'] == -1:
                self.points[i]['mileage'] = self.find_mileage(self.points[i]['lat'], self.points[i]['lon'], ignore=True)
                print(self.points[i])
        print(self.points)

    def get_points(self, ktype=None, kclass=None):
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
        for i in self.points:
            print(i)

    def find_mileage(self, latitude, longitude, ignore=False):
        mileage = close1 = close2 = -1
        distance1 = distance2 = 99999
        # Find the two closest points
        for i in range(0, len(self.points)):
            if 'lat' not in self.points[i] or 'lon' not in self.points[i] or self.points[i]['mileage'] == -1:
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

        # swap points so point 1 has lower mileage
        if self.points[close2]['mileage'] < self.points[close1]['mileage']:
            (close1, close2) = util.swap(close1, close2)
            (distance1, distance2) = util.swap(distance1, distance2)

        print(self.points[close1])
        print(self.points[close2])
        print(distance1)
        print(distance2)

        try:
            if distance1 == 0:
                print("point1")
                mileage = self.points[close1]['mileage']
            elif distance2 == 0:
                print("point2")
                mileage = self.points[close2]['mileage']
            elif distance3 < distance1 and distance2 < distance1:
                print("after")
                mileage = (self.points[close2]['mileage'] + distance2 +
                           self.points[close1]['mileage'] + distance1) / 2.0
            elif distance3 < distance2 and distance1 < distance2:
                print("before")
                mileage = (self.points[close1]['mileage'] - distance1 +
                           self.points[close2]['mileage'] - distance2) / 2.0
            elif distance1 < distance3 and distance2 < distance3:
                print("between")
                mileage = self.points[close1]['mileage'] + \
                    distance1 * (self.points[close2]['mileage'] -
                                 self.points[close1]['mileage']) / \
                    (distance1 + distance2)
            else:
                pass
        except ZeroDivisionError as ex:
            print(ex)
            pass

        return mileage

    def sanity_check(self, update=False):
        retval = True
        for i in range(0, len(self.points)):
            point = self.points[i]
            if 'lat' in point and 'lon' in point and 'mileage' in point:
                m = self.find_mileage(point['lat'],
                                      point['lon'],
                                      ignore=True)
                if abs(m - point['mileage']) > 0.01:
                    retval = False
                    if update:
                        self.points[i]['mileage'] = round(m, 2)
            else:
                print(point)

        return retval

if __name__ == "__main__":
    G = Gps2Miles("../known/mb.csv")
    #print(G.sanity_check(update=True))
    #G.dump()
    print(G.find_mileage(42.986304,-71.936522, ignore=True))
