import geo
import util

class Gps2Miles:

    def __init__(self, known_points):
        data = []
        with open(known_points, "r") as f:
            for line in f:
                if line[0] == "#":
                    continue
                items = line.split(",")
                try:
                    obj = {
                        'latitude': float(items[1]),
                        'longitude': float(items[2]),
                        'mileage': float(items[3]),
                    }
                except ValueError as ex:
                    continue
                data.append(obj)

        self.points = sorted(data, key=lambda k: k['mileage'], reverse=False)

    def dump(self):
        for i in self.points:
            print(i)

    def find_mileage(self, latitude, longitude, ignore=False):
        mileage = close1 = close2 = -1
        distance1 = distance2 = 99999
        # Find the two closest points
        for i in range(0, len(self.points)):
            if ignore and \
               latitude == self.points[i]['latitude'] and \
               longitude == self.points[i]['longitude']:
                continue
            distance = geo.great_circle(self.points[i]['latitude'],
                                        self.points[i]['longitude'],
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
        distance3 = geo.great_circle(self.points[close1]['latitude'],
                                     self.points[close1]['longitude'],
                                     self.points[close2]['latitude'],
                                     self.points[close2]['longitude'])

        # swap points so point 1 has lower mileage
        if self.points[close2]['mileage'] < self.points[close1]['mileage']:
            (close1, close2) = util.swap(close1, close2)
            (distance1, distance2) = util.swap(distance1, distance2)

        try:
            if distance1 == 0:
                #print("point1")
                mileage = self.points[close1]['mileage']
            elif distance2 == 0:
                #print("point2")
                mileage = self.points[close2]['mileage']
            elif distance3 < distance1 and distance2 < distance1:
                #print("after")
                mileage = (self.points[close2]['mileage'] + distance2 +
                           self.points[close1]['mileage'] + distance1) / 2.0
            elif distance3 < distance2 and distance1 < distance2:
                #print("before")
                mileage = (self.points[close1]['mileage'] - distance1 +
                           self.points[close2]['mileage'] - distance2) / 2.0
            elif distance1 < distance3 and distance2 < distance3:
                #print("between")
                mileage = self.points[close1]['mileage'] + \
                    distance1 * (self.points[close2]['mileage'] -
                                 self.points[close1]['mileage']) / \
                    (distance1 + distance2)
            else:
                pass
        except ZeroDivisionError:
            pass

        return mileage

    def sanity_check(self, update=False):
        retval = True
        for i in range(0, len(self.points)):
            point = self.points[i]
            m = self.find_mileage(point['latitude'],
                                  point['longitude'],
                                  ignore=True)
            if abs(m - point['mileage']) > 0.01:
                retval = False
                if update:
                    self.points[i]['mileage'] = round(m, 2)

        return retval

if __name__ == "__main__":
    G = Gps2Miles("../data/known_negs.csv")
    print(G.sanity_check(update=True))
    G.dump()
    print(G.find_mileage(43.441872, -71.593838, ignore=True))
