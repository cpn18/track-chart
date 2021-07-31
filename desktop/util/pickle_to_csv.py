#!/usr/bin/env python
import sys
import pickle
import json

with open(sys.argv[1], "rb") as f:
    data = pickle.load(f)

data = sorted(data, key=lambda k: k['time'], reverse=False)

for obj in data:
    print("%s %s %s *" % (obj['time'], obj['type'], json.dumps(obj)))
