#!/usr/bin/env python3
"""
Add Mileage and GPS locations to all objects
"""
import os
import json
import sys
import gps_to_mileage

import pirail

# Calculate mileage from GPS location
GET_MILEAGE_FROM_GPS = False

def add_mileage_and_gps(json_file, known_file, output_file):
    """
    Add GPS and mileage data to all elements
    """
    acclist = []
    last_tpv = {}
    gps = gps_to_mileage.Gps2Miles(known_file)
    with open(output_file, "w") as output:
        for _line_no, obj in pirail.read(json_file):
            if obj['class'] in ["SKY", "ATT", "LIDAR", "LPCM", "LIDAR3D"]:
                acclist.append(obj)

            if obj['class'] != "TPV":
                continue

            obj['mileage'], obj['certainty'] = gps.find_mileage(obj['lat'], obj['lon'])
            if len(last_tpv) != 0:
                if obj['time'] == last_tpv['time']:
                    continue

                # Ensure that altitude is set to something
                if not 'alt' in obj:
                    try:
                        obj['alt'] = last_tpv['alt']
                    except KeyError:
                        obj['alt'] = last_tpv['alt'] = 0

                time_start = pirail.parse_time_in_seconds(obj['time'])
                time_delta = time_start - pirail.parse_time_in_seconds(last_tpv['time'])
                if len(acclist) > 0:
                    delta_mileage = (obj['mileage'] - last_tpv['mileage'])
                    delta_lat = (obj['lat'] - last_tpv['lat'])
                    delta_lon = (obj['lon'] - last_tpv['lon'])
                    delta_alt = (obj['alt'] - last_tpv['alt'])
                    #print ("delta_lat", delta_lat)
                    #print ("delta_lon", delta_lon)
                    #print ("time_delta", time_delta.total_seconds())
                    for acc in acclist:
                        acc_time = pirail.parse_time_in_seconds(acc['time'])

                        millsec = (acc_time - time_start) / time_delta

                        acc['lat'] = last_tpv['lat'] + millsec*delta_lat
                        acc['lon'] = last_tpv['lon'] + millsec*delta_lon
                        acc['alt'] = last_tpv['alt'] + millsec*delta_alt

                        if GET_MILEAGE_FROM_GPS:
                            acc['mileage'], acc['certainty'] = gps.find_mileage(acc['lat'], acc['lon'])
                        else:
                            acc['mileage'] = last_tpv['mileage'] + millsec*delta_mileage
                            acc['certainty'] = obj['certainty'] * last_tpv['certainty']

                        output.write(json.dumps(acc))
                        output.write("\n")

            output.write(json.dumps(obj))
            output.write("\n")
            last_tpv = obj
            acclist = []

    print("Leftover elements = %d" % len(acclist))

def get_output_filename(input_file):
    """ Build Outout Filename """
    output_filename, output_extension = input_file.split('.',1)
    return "%s_with_mileage_sort_by_time.%s" % (
        output_filename,
        output_extension,
    )

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("USAGE: %s [args] json_file known_file" % sys.argv[0])
        sys.exit(1)

    INPUT_FILE = os.path.abspath(sys.argv[-2])
    KNOWN_FILE = sys.argv[-1]
    OUTPUT_FILE = get_output_filename(INPUT_FILE)

    add_mileage_and_gps(INPUT_FILE, KNOWN_FILE, OUTPUT_FILE)
