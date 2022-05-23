"""
UNH Capstone 2022 Project

Ben Grimes, Jeff Fernandes, Max Hennessey, Liqi Li
"""
import pirail
import json
import os
import statistics

#---Local Variables---
loc_average_acc_x = 0.0
loc_average_acc_y = 0.0
loc_average_acc_z = 0.0
loc_average_roll = 0.0
loc_average_pitch = 0.0
loc_average_yaw = 0.0


#TODO expand statistics tracked
def write_all_stats_json_file(path_to_read_file, path_to_new_file):
    None

def dump(read_file,write_file):
    if os.path.isfile(write_file):
        return

    averages = write_average_json_file(read_file)
    loc_average_acc_x = averages[0]
    loc_average_acc_y = averages[1]
    loc_average_acc_z = averages[2]
    loc_average_roll = averages[3]
    loc_average_pitch = averages[4]
    loc_average_yaw = averages[5]

    minX = write_min(read_file, "acc_x")
    maxX = write_max(read_file, "acc_x")
    minY = write_min(read_file, "acc_y")
    maxY = write_max(read_file, "acc_y")
    minZ = write_min(read_file, "acc_z")
    maxZ = write_max(read_file, "acc_z")
    minRoll = write_min(read_file, "roll")
    maxRoll = write_max(read_file, "roll")
    minPitch = write_min(read_file, "pitch")
    maxPitch = write_max(read_file, "pitch")
    minYaw = write_min(read_file, "yaw")
    maxYaw = write_max(read_file, "yaw")

    sd_X = write_sd(read_file, "acc_x")
    sd_Y = write_sd(read_file, "acc_y")
    sd_Z = write_sd(read_file, "acc_z")
    sd_roll = write_sd(read_file, "roll")
    sd_pitch = write_sd(read_file, "pitch")
    sd_yaw = write_sd(read_file, "yaw")

    d = {
        "average_acc_x": loc_average_acc_x, "average_acc_y": loc_average_acc_y, "average_acc_z": loc_average_acc_z,
        "average_roll": loc_average_roll, "average_pitch": loc_average_pitch, "average_yaw": loc_average_yaw,
        "minimum_x": minX, "maximum_x": maxX, "minimum_y": minY, "maximum_y": maxY, "minimum_z": minZ,
        "maximum_z": maxZ, "minimum_roll": minRoll, "maximum_roll": maxRoll, "minimum_pitch": minPitch,
        "maximum_pitch": maxPitch, "minimum_yaw": minYaw, "maximum_yaw": maxYaw, "standard_dev_x": sd_X,
        "standard_dev_y": sd_Y, "standard_dev_z": sd_Z, "standard_dev_roll": sd_roll, "standard_dev_pitch": sd_pitch,
        "standard_dev_yaw": sd_yaw,
    }
    with open(write_file, 'w') as f:
        json.dump(d, f, indent=1)


def write_average_json_file(path_to_read_file):

    average_acc_x = 0.0
    average_acc_y = 0.0
    average_acc_z = 0.0
    average_roll = 0.0
    average_pitch = 0.0
    average_yaw = 0.0

    N = 0.0
    for line_no, obj in pirail.read('../web_server_flask/'+path_to_read_file):

        N += 1
        average_acc_x += obj["acc_x"]
        average_acc_y += obj["acc_y"]
        average_acc_z += obj["acc_z"]
        average_roll += obj["roll"]
        average_pitch += obj["pitch"]
        average_yaw += obj["yaw"]

    loc_average_acc_x = average_acc_x/N
    loc_average_acc_y = average_acc_y/N
    average_acc_z = average_acc_z/N
    average_roll = average_roll/N
    average_pitch = average_pitch/N
    average_yaw = average_yaw/N

    return loc_average_acc_x,loc_average_acc_y,average_acc_z,average_roll,average_pitch,average_yaw

def write_min(read_file,json_name):
    list = []

    for num,obj in pirail.read('../web_server_flask/' + read_file):
        list.append(obj[json_name])
    #print(list)

    minList = min(list)
    return minList

def write_max(read_file,json_name):
    list = []

    for num,obj in pirail.read('../web_server_flask/' + read_file):
        list.append(obj[json_name])
    #print(list)

    maxList = max(list)
    return maxList

def write_sd(read_file,json_name):
    list = []

    for num,obj in pirail.read('../web_server_flask/' + read_file):
        list.append(obj[json_name])

    sd = statistics.stdev(list)
    return sd


