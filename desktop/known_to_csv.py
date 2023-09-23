#!/usr/bin/env python3
import os
import sys
import json
import datetime
import argparse
import gps_to_mileage


def export_to_csv(args):
    """ Export Points to CSV File """

    def write_geo(out, point):
        out.write(str(point.get('lat', '')) + "," + str(point.get('lon', '')) + ",")

    def write_mileage(out, point):
        out.write(str(point.get('mileage', '')) + ",")

    def write_survey_val(out, point):
        out.write(str(point['metadata'].get('survey', '')) + "," + str(point['metadata'].get('val', '')) + ",")

    def write_eol(out):
        out.write("\n")

    output_filename = os.path.basename(args.known_file)
    G = gps_to_mileage.Gps2Miles(args.known_file)

    if not args.overwrite and os.path.exists(output_filename):
        print("Output file exists")
        sys.exit(1)

    with open(output_filename, "w") as out:
        out.write("Name: " + output_filename + "\n")
        out.write("Description: (c)" + str(datetime.date.today().year) + " PiRail -- https://www.facebook.com/PiRailNH\n")
        out.write("Latitude,Longitude,Mileage,Survey,ValChart,Description\n")

        for point in G.points:

            if args.mile_posts and point['class'] == 'MP':
                write_geo(out, point)
                write_mileage(out, point)
                write_survey_val(out, point)
                out.write(point['metadata']['name'] + "/" + point['metadata']['alt_name'])
                write_eol(out)

            if args.overpass and point['class'] == 'O':
                write_geo(out, point)
                write_mileage(out, point)
                write_survey_val(out, point)
                out.write(point['metadata'].get('name',''))
                write_eol(out)


def main():
    parser = argparse.ArgumentParser(description='Export Known Point to CSV')
    parser.add_argument('known_file')
    parser.add_argument('--mile-posts', action='store_true')
    parser.add_argument('--overpass', action='store_true')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()

    export_to_csv(args)

if __name__ == "__main__":
    main()
