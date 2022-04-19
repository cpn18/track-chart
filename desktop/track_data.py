import math
from os import stat
import statistics
import copy
import os.path
from desktop import gps_to_mileage, pirail
from desktop.acceleration_gyroscopic_data import acceleration_gyroscopic_data
import pickle

mileageToData = {}
AA = 0.40  # Complementary filter constant


def json_to_dict_mileage(data_file, known_file):
    if os.path.exists(data_file + ".pickle"):
        return pickle_to_dict_mileage(data_file + ".pickle")

    gyroXangle = gyroYangle = gyroZangle = CFangleX = CFangleY = CFangleZ = 0
    last_time = None
    for line_no, obj in pirail.read(data_file):
        if obj['class'] != "ATT":
            continue
        if 'roll' in obj and 'yaw' in obj and 'pitch' in obj:
            mileage = obj['mileage']
            mileageToData[mileage] = acceleration_gyroscopic_data(obj['acc_x'], obj['acc_y'], obj['acc_z'], obj['roll'],
                                                                  obj['pitch'], obj['yaw'])
            continue

        if last_time is not None:
            DT = (pirail.parse_time(obj['time']) - pirail.parse_time(last_time)).total_seconds()
            last_time = obj['time']
        else:
            DT = 0

        # Calculate Yaw/Pitch/Roll
        # Based on:
        # https://github.com/ozzmaker/BerryIMU/blob/master/python-BerryIMU-gryo-accel-compass/berryIMU-simple.py
        gyroXangle += obj['gyro_x'] * DT;
        gyroYangle += obj['gyro_y'] * DT;
        gyroZangle += obj['gyro_z'] * DT;
        AccXangle = math.degrees((float)(math.atan2(obj['acc_y'], obj['acc_z']) + math.pi));
        AccYangle = math.degrees((float)(math.atan2(obj['acc_z'], obj['acc_x']) + math.pi));
        AccZangle = math.degrees((float)(math.atan2(obj['acc_y'], obj['acc_x']) + math.pi));
        # Complementary Filter
        CFangleX = AA * (CFangleX + obj['gyro_x'] * DT) + (1 - AA) * AccXangle;
        CFangleY = AA * (CFangleY + obj['gyro_y'] * DT) + (1 - AA) * AccYangle;
        CFangleZ = AA * (CFangleZ + obj['gyro_z'] * DT) + (1 - AA) * AccZangle;

        if 'mileage' not in obj:
            if 'lat' in obj and 'lon' in obj:
                obj['mileage'], obj['certainty'] = gps_to_mileage.Gps2Miles(known_file).find_mileage(
                    obj['lat'], obj['lon'])
        mileageToData[obj['mileage']] = acceleration_gyroscopic_data(AccXangle, AccYangle, AccZangle, CFangleY,
                                                                     CFangleX, CFangleZ)

    with open(data_file + ".pickle", "wb") as f:
        pickle.dump(mileageToData, f, pickle.HIGHEST_PROTOCOL)
    return mileageToData


def pickle_to_dict_mileage(data_file):
    with open(data_file, "rb") as f:
        mileageToData = pickle.load(f)
    return mileageToData


def select_range(track: dict, start: int, end: int):
    delete = [key for key in track if (key < start or key > end)]
    newRange = copy.deepcopy(track)
    for key in delete: del newRange[key]
    if len(newRange) == 0:
        raise Exception("The provided range {} to {} is not valid".format(start, end))
    return newRange

#---------Average---------
def calc_average_acceleration_gyro(track: dict):
    average_accX = average_accY = average_accZ = average_roll = average_pitch = average_yaw = 0
    n = len(track.values())

    for data_point in track.values():
        average_accX += data_point.get_accX()
        average_accY += data_point.get_accY()
        average_accZ += data_point.get_accZ()
        average_roll += data_point.get_roll()
        average_pitch += data_point.get_pitch()
        average_yaw += data_point.get_yaw()

    return acceleration_gyroscopic_data(average_accX / n, average_accY / n, average_accZ / n, average_roll / n,
                                        average_pitch / n, average_yaw / n)

#--------Standard Deviation---------
def calc_standard_deviation_all(track: dict):
    list_x = []
    list_y = []
    list_z = []
    list_roll = []
    list_pitch = []
    list_yaw = []

    for data_point in track.values():
        list_x.append(data_point.get_accX())
        list_y.append(data_point.get_accY())
        list_z.append(data_point.get_accZ())
        list_roll.append(data_point.get_roll())
        list_pitch.append(data_point.get_pitch())
        list_yaw.append(data_point.get_yaw())



    sd_x = statistics.stdev(list_x)
    sd_y = statistics.stdev(list_y)
    sd_z = statistics.stdev(list_z)
    sd_roll = statistics.stdev(list_roll)
    sd_pitch = statistics.stdev(list_pitch)
    sd_yaw = statistics.stdev(list_yaw)

    return acceleration_gyroscopic_data( sd_x, sd_y, sd_z, sd_roll, sd_pitch, sd_yaw)

#---------Min Values----------
'''
def get_minX(track:dict):
    x_vals = []

    for data_point in track.values():
        x_vals.append(data_point.get_accX())

    return acceleration_gyroscopic_data(min(x_vals))

def get_minY(track:dict):
    y_vals = []

    for data_point in track.values():
        y_vals.append(data_point.get_accY())

    return acceleration_gyroscopic_data(min(y_vals))

def get_minZ(track:dict):
    z_vals = []

    for data_point in track.values():
        z_vals.append(data_point.get_accZ())

    return acceleration_gyroscopic_data(min(z_vals))

def get_minRoll(track:dict):
    roll_vals = []

    for data_point in track.values():
        roll_vals.append(data_point.get_roll())

    return acceleration_gyroscopic_data(min(roll_vals))

def get_minPitch(track:dict):
    pitch_vals = []

    for data_point in track.values():
        pitch_vals.append(data_point.get_pitch())

    return acceleration_gyroscopic_data(min(pitch_vals))

def get_minYaw(track:dict):
    yaw_vals = []

    for data_point in track.values():
        yaw_vals.append(data_point.get_yaw())

    return acceleration_gyroscopic_data(min(yaw_vals))
'''
def get_minAll(track:dict):
    list_x = []
    list_y = []
    list_z = []
    list_roll = []
    list_pitch = []
    list_yaw = []

    for data_point in track.values():
        list_x.append(data_point.get_accX())
        list_y.append(data_point.get_accY())
        list_z.append(data_point.get_accZ())
        list_roll.append(data_point.get_roll())
        list_pitch.append(data_point.get_pitch())
        list_yaw.append(data_point.get_yaw())

    sd_x = min(list_x)
    sd_y = min(list_y)
    sd_z = min(list_z)
    sd_roll = min(list_roll)
    sd_pitch = min(list_pitch)
    sd_yaw = min(list_yaw)

    return acceleration_gyroscopic_data( sd_x, sd_y, sd_z, sd_roll, sd_pitch, sd_yaw)

#----------Max Values-----------
'''
def get_maxX(track:dict):
    x_vals = []

    for data_point in track.values():
        x_vals.append(data_point.get_accX())

    return acceleration_gyroscopic_data(max(x_vals))

def get_maxY(track:dict):
    y_vals = []

    for data_point in track.values():
        y_vals.append(data_point.get_accY())

    return acceleration_gyroscopic_data(max(y_vals))

def get_maxZ(track:dict):
    z_vals = []

    for data_point in track.values():
        z_vals.append(data_point.get_accZ())

    return acceleration_gyroscopic_data(max(z_vals))

def get_maxRoll(track:dict):
    roll_vals = []

    for data_point in track.values():
        roll_vals.append(data_point.get_roll())

    return acceleration_gyroscopic_data(max(roll_vals))

def get_maxPitch(track:dict):
    pitch_vals = []

    for data_point in track.values():
        pitch_vals.append(data_point.get_pitch())

    return acceleration_gyroscopic_data(max(pitch_vals))

def get_maxYaw(track:dict):
    yaw_vals = []

    for data_point in track.values():
        yaw_vals.append(data_point.get_yaw())

    return acceleration_gyroscopic_data(max(yaw_vals))
'''
def get_maxAll(track:dict):
    list_x = []
    list_y = []
    list_z = []
    list_roll = []
    list_pitch = []
    list_yaw = []

    for data_point in track.values():
        list_x.append(data_point.get_accX())
        list_y.append(data_point.get_accY())
        list_z.append(data_point.get_accZ())
        list_roll.append(data_point.get_roll())
        list_pitch.append(data_point.get_pitch())
        list_yaw.append(data_point.get_yaw())

    sd_x = max(list_x)
    sd_y = max(list_y)
    sd_z = max(list_z)
    sd_roll = max(list_roll)
    sd_pitch = max(list_pitch)
    sd_yaw = max(list_yaw)

    return acceleration_gyroscopic_data( sd_x, sd_y, sd_z, sd_roll, sd_pitch, sd_yaw)

#------FINDING OUTLIERS--------
def getOutlierX(track: dict):
    list_x = []
    outliers = []
    ave_x = 0

    for data_point in track.values():
        list_x.append(data_point.get_accX())
        ave_x += data_point.get_accX()

    n = len(list_x)
    average = ave_x / n

    #Move outliers from list_x to outlier list
    for num in list_x:
        if num > average + 15 or num < average - 15:
            outliers.append(num)

    return outliers

def getOutlierY(track: dict):
    list_y = []
    outliers = []
    ave_y = 0

    for data_point in track.values():
        list_y.append(data_point.get_accY())
        ave_y += data_point.get_accY()

    n = len(list_y)
    average = ave_y / n

    #Move outliers from list_y to outlier list
    for num in list_y:
        if num > average + 15 or num < average - 15:
            outliers.append(num)

    return outliers

def getOutlierZ(track: dict):
    list_z = []
    outliers = []
    ave_z = 0

    for data_point in track.values():
        list_z.append(data_point.get_accZ())
        ave_z += data_point.get_accZ()

    n = len(list_z)
    average = ave_z / n

    #Move outliers from list_z to outlier list
    for num in list_z:
        if num > average + 50 or num < average - 50:
            outliers.append(num)

    return outliers

def getOutlierRoll(track: dict):
    list_roll = []
    outliers = []
    ave_roll = 0

    for data_point in track.values():
        list_roll.append(data_point.get_roll())
        ave_roll += data_point.get_roll()

    n = len(list_roll)
    average = ave_roll / n

    #Move outliers from list_roll to outlier list
    for num in list_roll:
        if num > average + 16 or num < average - 23:
            outliers.append(num)

    return outliers

def getOutlierPitch(track: dict):
    list_p = []
    outliers = []
    ave_p = 0

    for data_point in track.values():
        list_p.append(data_point.get_pitch())
        ave_p += data_point.get_pitch()

    n = len(list_p)
    average = ave_p / n

    #Move outliers from list_p to outlier list
    for num in list_p:
        if num > average + 12 or num < average - 20:
            outliers.append(num)

    return outliers

def getOutlierYaw(track: dict):
    list_y = []
    outliers = []
    ave_y = 0

    for data_point in track.values():
        list_y.append(data_point.get_yaw())
        ave_y += data_point.get_yaw()

    n = len(list_y)
    average = ave_y / n

    #Move outliers from list_p to outlier list
    for num in list_y:
        if num > average + 52 or num < average - 50:
            outliers.append(num)

    return outliers


