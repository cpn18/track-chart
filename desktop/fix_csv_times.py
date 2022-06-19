#!/usr/bin/env python3
"""
Fix localtime offset

Only needed if the local system time was other than
UTC.  We found that one upgrade had changed the system
to BST, and was one hour off.
"""
import sys
import json
from datetime import timedelta
from dateutil.parser import parse

HOUR=-1

# Records to skip; ie, has correct time
SKIP=["TPV"]

def new_time(timestamp):
    """ Calculate new timestamp """
    retval = parse(timestamp, fuzzy=True)
    retval += timedelta(hours=HOUR)
    retval = str(retval).replace(" ", "T").replace("+00:00", "Z")
    return retval

def alter_time(filename):
    """ Alter timestamps in files """
    output = filename + ".new"
    with open(output, "w") as f_out:
        with open(filename, "r") as f_in:
            for line in f_in:
                line = line.rstrip()
                fields = line.split(" ")
                key = fields[1]

                if key in SKIP:
                    f_out.write(line+"\n")
                else:
                    timestamp = fields[0]
                    data = json.loads(" ".join(fields[2:-1]))
                    timestamp = new_time(timestamp)
                    if 'time' in data:
                        data['time'] = timestamp
                    f_out.write("%s %s %s *\n" % (timestamp, key, json.dumps(data)))
    os.rename(filename, output)

if __name__ == "__main__":
    for f in sys.argv[1:]:
        alter_time(f)
