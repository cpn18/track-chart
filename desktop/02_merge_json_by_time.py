#!/usr/bin/env python3
"""
Merge sort the JSON files

Assumes that files presored by FIELD
"""
import sys
import json

FIELD="time"

def parse_line(input_line):
    """ Try to parse a line as JSON, fallback to Python eval """
    try:
        data = json.loads(input_line)
    except json.decoder.JSONDecodeError:
        # Oops. Not JSON? Maybe a Python string?
        data = eval(input_line)
    # Change to six digits to enable string sorting
    data['time'] = data['time'].replace('.000Z', '.000000Z')
    return data

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
            data[i] = parse_line(new_data)
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
                min_index = i

        # Output the line
        print(json.dumps(data[min_index]))

        # Read next line from same file
        new_data = input_files[min_index].readline()
        if new_data != "":
            data[min_index] = parse_line(new_data)
        else:
            input_files[min_index].close()
            data[min_index] = input_files[min_index] = None
            valid -= 1

if __name__ == "__main__":
    merge_sort(sys.argv[1:], FIELD)
