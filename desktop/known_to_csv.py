#!/usr/bin/env python
import os
import sys
import json
import datetime
import gps_to_mileage


def export_to_csv(input_filename):
    output_filename = os.path.basename(sys.argv[1])
    G = gps_to_mileage.Gps2Miles(input_filename)

    if os.path.exists(output_filename):
        print("Output file exists")
        sys.exit(1)

    with open(output_filename, "w") as out:
        out.write("Name: " + output_filename + "\n")
        out.write("Description: (c)" + str(datetime.date.today().year) + " PiRail -- https://www.facebook.com/PiRailNH\n")

        for point in G.points:
            if point['class'] == 'MP' and 'lat' in point:
                out.write(str(point['lat']) + "," + str(point['lon']) + ",")
                out.write(point['metadata']['name'] + "/" + point['metadata']['alt_name'] + "\n")

if __name__ == "__main__":
    input_filename = sys.argv[1]
    export_to_csv(input_filename)
