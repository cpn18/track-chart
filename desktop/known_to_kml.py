import os
import sys
import json
import datetime
import gps_to_mileage


def export_to_kml(input_filename):
    output_filename = os.path.basename(sys.argv[1]).replace(".csv", ".kml")
    G = gps_to_mileage.Gps2Miles(input_filename)

    with open(output_filename, "w") as out:
        out.write("<?xml version=\"1.0\" encoding=\"UTF-8i\"?>\n")
        out.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
        out.write("  <Document>\n")
        out.write("    <name>" + output_filename + "</name>\n")
        out.write("    <description>(c)" + str(datetime.date.today().year) + " PiRail -- https://www.facebook.com/PiRailNH</description>\n")

        for point in G.points:
            if point['class'] == 'MP' and 'lat' in point:
                out.write("    <Placemark>\n")
                out.write("      <name>" + point['metadata']['name'] + "/" + point['metadata']['alt_name'] + "</name>\n")
                out.write("      <description>"+json.dumps(point)+"</description>\n")
                out.write("      <Point>\n")
                out.write("        <coordinates>" + str(point['lon']) + "," + str(point['lat']) + "</coordinates>\n")
                out.write("      </Point>\n")
                out.write("    </Placemark>\n")
        out.write("  </Document>\n")
        out.write("</kml>\n")

if __name__ == "__main__":
    input_filename = sys.argv[1]
    export_to_kml(input_filename)
