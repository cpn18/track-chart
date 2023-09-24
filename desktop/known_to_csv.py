#!/usr/bin/env python3
import os
import sys
import json
import datetime
import argparse
import gps_to_mileage

DEFAULT_CLASSES = "MP,O,X"

def export_to_csv(args):
    """ Export Points to CSV File """

    def write_geo(out, point):
        out.write(str(point.get('lat', '')))
        out.write(",")
        out.write(str(point.get('lon', '')))
        out.write(",")

    def write_mileage(out, point):
        mileage = point.get('mileage', '')
        if mileage != "":
            mileage = "%0.3f" % mileage
        if mileage[-1] == "0":
            mileage = mileage[0:-1]
        out.write(mileage)
        out.write(",")

    def write_survey_val(out, point):
        out.write(str(point['metadata'].get('survey', '')))
        out.write(",")
        out.write(str(point['metadata'].get('val', '')))
        out.write(",")

    def write_name(out, point, extra=""):
        out.write(point['class'])
        out.write(",")
        out.write(point['metadata'].get('name', ''))
        if 'alt_name' in point['metadata']:
            out.write("/")
            out.write(point['metadata']['alt_name'])
        if extra != "":
            out.write(",")
            out.write(extra)

    def write_eol(out):
        out.write("\n")

    output_filename = os.path.basename(args.known_file)
    G = gps_to_mileage.Gps2Miles(args.known_file)

    if not args.overwrite and os.path.exists(output_filename):
        print("Output file exists")
        sys.exit(1)

    with open(output_filename, "w") as out:
        out.write("Name: ")
        out.write(output_filename)
        out.write("\n")
        out.write("Description: (c)")
        out.write(str(datetime.date.today().year))
        out.write(" PiRail -- https://www.facebook.com/PiRailNH\n")
        out.write("Latitude,Longitude,Mileage,Survey,ValChart,Class,Description,Extra\n")

        classes = args.classes.split(',')

        for point in G.points:

            if point['class'] in classes:
                write_geo(out, point)
                write_mileage(out, point)
                write_survey_val(out, point)
                write_name(out, point)
                write_eol(out)

def main():
    parser = argparse.ArgumentParser(description='Export Known Point to CSV')
    parser.add_argument('known_file', help="Path to the 'Known Points' file")
    parser.add_argument('-c', '--classes', type=str, default=DEFAULT_CLASSES, help="Classes of points to export (%s)" % DEFAULT_CLASSES)
    parser.add_argument('--overwrite', action='store_true', help="Allow overwrite of existing file")
    args = parser.parse_args()

    export_to_csv(args)

if __name__ == "__main__":
    main()
