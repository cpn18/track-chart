#!/usr/bin/env python3
"""
Merge sort the JSON files

Assumes that files presored by FIELD
"""
import sys
import json

FIELD="time"

def merge_sort(filenames, field):
    """ Merge Sort JSON Files """

    # Open the Files
    input_files = []
    for filename in filenames:
        input_files.append(open(filename))
    valid = count = len(input_files)

    # Read initial lines
    data = [None] * count
    for i in range(count):
        new_data = input_files[i].readline()
        if new_data != "":
            data[i] = json.loads(new_data)
        else:
            input_files[i].close()
            data[i] = input_files[i] = None
            valid -= 1

    while valid > 0:

        # Look for minimum value
        min_value = None
        min_index = 0
        for i in range(count):
            if data[i] is None:
                continue
            if min_value is None or data[i][field] < min_value:
                min_value = data[i][field]
                min_i = i

        # Output the line
        print(json.dumps(data[min_i]))

        # Read next line from same file
        new_data = input_files[min_i].readline()
        if new_data != "":
            data[min_i] = json.loads(new_data)
        else:
            input_files[min_i].close()
            data[min_i] = input_files[min_i] = None
            valid -= 1

if __name__ == "__main__":
    merge_sort(sys.argv[1:], FIELD)
