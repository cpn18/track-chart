#!/usr/bin/env python3
import sys
import json
import pickle

with open(sys.argv[1], "r") as f:
    data = json.loads(f.read())

with open(sys.argv[2] + ".pickle", "wb" ) as f:
    pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

