import re
import json
import pandas as pd

def read_IMU_to_file(infilepath, outfilepath):
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
            data[i] = json_data
        except AttributeError:
            continue

    in_file.close()

    df = pd.DataFrame(data)
    print(df)

    df.to_csv(outfilepath)



