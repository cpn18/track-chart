"""
UNH Capstone 2022 Project

Ben Grimes, Jeff Fernandes, Max Hennessey, Liqi Li
"""

import os
import pirail
import re
import json

def write_json_data_to_range(pathToRange, locationPath, minRange, maxRange):
    data = []
    for line_no, obj in pirail.read('../web_server_flask/'+locationPath):
        if obj["mileage"] >= minRange and obj["mileage"] <= maxRange:
            data.append(obj)

    data = sorted(data, key=lambda k: k["mileage"], reverse=False)
    #print(os.path.isfile(pathToRange))
    f = open(pathToRange, 'x')
    for obj in data:
        j = re.sub(r"'", '"', str(obj))
        f.write(j+'\n')
    f.close()

