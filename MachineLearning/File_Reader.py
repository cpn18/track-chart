import re
import json
import pandas as pd

def read_IMU_to_file(infilepath, outfilepath): # used for reading an _imu csv file
    in_file = open(infilepath, 'r')

    # Skip first two lines, they are config information
    lines = in_file.readlines()[2:]

    data = [{} for _ in range(len(lines))]

    for i in range(len(lines)):
        if i % 1000 == 0:
            print(f"Reading Data... ({i}/{len(lines)})")
        try:
            json_string = re.search("(\{.+?\}) *", lines[i]).group(1)
            json_data = json.loads(json_string)
            if i % 10000 == 0:
                print(json_data)
            data[i] = json_data
        except AttributeError:
            continue

    in_file.close()

    df = pd.DataFrame(data)
    print(df)

    df.to_csv(outfilepath, index=False)

def read_mixed_json_to_file(infilepath, outfilepath): # used for a json file beginning with wrr, containing entries for TPV, ATT, and SKY
    in_file = open(infilepath, 'r')

    lines = in_file.readlines()

    data = []

    current_tpv = {}

    for i in range(len(lines)):
        if i % 1000 == 0:
            print(f"Reading Data... ({i}/{len(lines)})")

        try:
            entry = json.loads(lines[i])

            if 'class' in entry:
                if entry['class'] == 'TPV':
                    current_tpv = entry
                if entry['class'] == 'ATT':
                    if current_tpv != {}:
                        entry['speed'] = current_tpv['speed']

                        data.append(entry)
                # if entry['class'] == 'SKY':

        except AttributeError:
            continue

    

    df = pd.DataFrame(data)
    df.to_csv(outfilepath)


    



