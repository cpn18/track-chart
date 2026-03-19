#!/usr/bin/env python

import sys
import datetime
import json
import os
import signal
from multiprocessing import Process
import util
import time
import pytermgui as ptg
import psutil as psu
import traceback

CONFIG = """
config:
    Window:
        styles:
            border: 'ivory'
            corner: 'ivory'
"""
children = {}

def cleanup(sig, frame):
    clean_children()

def clean_children():
    for c_name, (c_pid, status) in children.items():
        os.kill(c_pid, signal.SIGINT)
        os.kill(c_pid, signal.SIGTERM)
        print("Launcher stopped process (" + str(c_name) + ", " + str(c_pid) + ")")

    print("Launcher stopped all launched processes\n")
    exit(0)

def get_children_status() -> str:
    global children
    status = children

    for p in psu.process_iter(['pid']):
        for c_name, (c_pid, c_status) in children.items():
            if p.info['pid'] == c_pid:
                status[c_name] = (c_pid, True)

    children = status

    res = ""
    for c_name, (c_pid, status) in status.items():
        res += "[/ bold]" + c_name + "[/] [/ italic](" + str(c_pid) + ")[/] " + ("[inverse lawngreen]Running\n" if status == True else "[inverse crimson]Stopped\n")

    return res

def launch(task):
    """ Launch a command """
    path = os.path.join(os.getcwd(), task['cmd'][0])
    args = task['cmd']
    for i in range(len(args)):
        if args[i] == "%OUTPUT_DIR%":
            args[i] = OUTPUT
        elif args[i] == "%PORT%":
            args[i] = str(task['tcp']['port'])
    #print(path, args)

    pid = os.fork()
    if pid != 0:
        children[task['cmd'][0]] = (pid, True)
        pass
    else:
        os.execv(path, args)
        sys.exit(-1)

def quit(manager: ptg.WindowManager) -> None:
    manager.stop()
    clean_children()

def launcher():
    # Prepare to clean child processes
    signal.signal(signal.SIGINT, cleanup)

    """ Launch all commands """
    config = util.read_config()

    for task in config:
        if isinstance(config[task], str):
            continue
        if config[task].get('cmd', None) is not None:
            if config[task].get('enable', True):
                launch(config[task])

    print(sys.argv)
    if len(sys.argv) > 1 and sys.argv[1] == "--background":
        sys.exit(0)

    time.sleep(1)
    with ptg.WindowManager() as manager:
        window = (
            ptg.Window(
                "Press [inverse crimson]Ctlr-C[/] To Exit",
                get_children_status(),
                "",
                # ["[inverse crimson]Exit", lambda *_: quit(manager)],
                width = 60,
                box = "DOUBLE"
            )
            .set_title("[bold crimson]PiRail Launcher")
            # .center()
        )
        manager.add(window)

if __name__ == "__main__":
    try:
        OUTPUT = sys.argv[-1]
    except IndexError:
        OUTPUT = os.path.join(os.getenv("HOME"), "gps-data")
    os.makedirs(OUTPUT, exist_ok=True)

    children = {}

    try:
        launcher()
    except Exception:
        print("Closing due to error: " + str(traceback.format_exc()))
        clean_children()
