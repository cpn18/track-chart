import sys
import datetime
import json
import os

def read_config():
    """ Read Configuration """
    try:
        with open("config.json", "r") as config_file:
            config = json.loads(config_file.read())
    except Exception as ex:
        print(ex)
        config = {
            "gps": {"log": True},
        }
    config['class'] = "CONFIG"
    config['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return config

def launch(task, output_directory):
    pid = os.fork()
    if pid != 0: # Parent
        pass
    else:        # Child
        path = os.path.join(os.getcwd(), task['cmd'][0])
        args = task['cmd']

        for i in range(len(args)):
            if args[i] == "%OUTPUT_DIR%":
                args[i] = output_directory

        #print(path, args)
        os.execv(path, args)
        sys.exit(-1)

def launcher(output_directory):
    config = read_config()

    for task in config:
        if 'cmd' in config[task]:
            if not 'enable' in config[task]:
                config[task]['enable'] = True
            if config[task]['enable']:
                launch(config[task], output_directory)

if __name__ == "__main__":
    try:
        OUTPUT = sys.argv[1]
    except IndexError:
        OUTPUT = "/root/gps-data"

    launcher(OUTPUT)
