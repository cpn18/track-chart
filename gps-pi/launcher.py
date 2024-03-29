#!/usr/bin/env python

import sys
import datetime
import json
import os

import util

def launch(task):
    """ Launch a command """
    path = os.path.join(os.getcwd(), task['cmd'][0])
    args = task['cmd']
    for i in range(len(args)):
        if args[i] == "%OUTPUT_DIR%":
            args[i] = OUTPUT
        elif args[i] == "%PORT%":
            args[i] = str(task['port'])
    #print(path, args)

    pid = os.fork()
    if pid != 0: # Parent
        pass
    else:        # Child
        os.execv(path, args)
        sys.exit(-1)

def launcher():
    """ Launch all commands """
    config = util.read_config()

    for task in config:
        if 'cmd' in config[task]:
            if not 'enable' in config[task]:
                config[task]['enable'] = True
            if config[task]['enable']:
                launch(config[task])

if __name__ == "__main__":
    try:
        OUTPUT = sys.argv[1]
    except IndexError:
        OUTPUT = "/root/gps-data"

    launcher()
