"""
UNH Capstone 2022 Project

Ben Grimes, Jeff Fernandes, Max Hennessey, Liqi Li
"""
import json
import csv
import math
import random
import numpy as np
import matplotlib.pyplot as plt

def create_json_from_csv(pathToFile, newFile):
    file_in = open(pathToFile, "r")

    lines = file_in.readlines()
    print("Reading")
    i = 0
    j = [{} for _ in range(lines.__len__())]
    for line in lines:
        d = json.loads(line)
        j[i] = d

        if i % 10000 == 0:
            print(i)
        i += 1

    with open(newFile, 'w') as outfile1:
        for row in j:
            print(json.dumps(row), file=outfile1)


def create_faux_data_for_test_train_from_json(pathToJson, CSVFileName, numberOfSamples: int):
    header = ["mileage", "acc_z", "acc_y", "acc_x", "pitch", "roll", "yaw", "damaged"]

    # WRITE TO NEW CSV FILE
    AA = .40
    with open(CSVFileName, 'w') as f:
        plt.rcParams['axes.facecolor'] = 'black'
        writer = csv.writer(f)
        writer.writerow(header)

        file_in1 = open(pathToJson, "r")
        lines1 = file_in1.readlines()

        xl1 = []
        ylz = []
        ylx = []
        yly = []
        ygp = []
        ygr = []
        ygy = []

        # PREPROCESS DATA FROM JSON FILE
        CFangleX = 0
        CFangleY = 0
        CFangleZ = 0
        for line in lines1:
            d = {}
            d = json.loads(line)
            if 'mileage' in d and 'acc_z' in d and 'acc_x' in d and 'acc_y' in d and 'pitch' in d and 'roll' in d and 'yaw' in d:
                xl1.append(d['mileage'])
                ylz.append( d['acc_z'])
                ylx.append( d['acc_x'])
                yly.append( d['acc_y'])
                ygp.append( d['pitch'])
                ygr.append( d['roll'])
                ygy.append( d['yaw'])
            elif 'mileage' in d and 'acc_z' in d and 'acc_x' in d and 'acc_y' in d and 'gyro_x' in d and 'gyro_y' in d and 'gyro_z' in d:
                xl1.append(d['mileage'])
                ylz.append( d['acc_z'])
                ylx.append( d['acc_x'])
                yly.append( d['acc_y'])

                accXAngle = math.degrees((float)(math.atan2(d['acc_y'], d['acc_z']) + math.pi))
                accYAngle = math.degrees((float)(math.atan2(d['acc_z'], d['acc_x']) + math.pi))
                accZAngle = math.degrees((float)(math.atan2(d['acc_y'], d['acc_x']) + math.pi))

                ygp.append( AA * (CFangleY + d['gyro_y'] ) + (1 - AA) * accYAngle)
                ygr.append(AA * (CFangleX + d['gyro_x']) + (1 - AA) * accXAngle)
                ygy.append( AA * (CFangleZ + d['gyro_z'] ) + (1 - AA) * accZAngle)

        file_in1.close()


        x1 = np.asarray(xl1)
        acc_z_ordered_collection = np.asarray(ylz)
        acc_y_ordered_collection = np.asarray(yly)
        acc_x_ordered_collection = np.asarray(ylx)
        pitch_ordered_collection = np.asarray(ygp)
        roll_ordered_collection = np.asarray(ygr)
        yaw_ordered_collection = np.asarray(ygy)

        # FIND OUTLIERS BASED ON Z LINEAR AXIS (12 standard deviations from mean in this case)

        mean = np.mean(acc_z_ordered_collection)
        std = np.std(acc_z_ordered_collection)
        std12 = std * 12.0

        xout = []
        acc_z_outliers = []
        acc_y_outliers = []
        acc_x_outliers = []
        pitch_outliers = []
        roll_outliers = []
        yaw_outliers = []
        i = 0
        for y in ylz:
            if y > (mean + std12):
                xout.append(x1[i])
                acc_z_outliers.append(acc_z_ordered_collection[i])
                acc_y_outliers.append(acc_y_ordered_collection[i])
                acc_x_outliers.append(acc_x_ordered_collection[i])
                pitch_outliers.append(pitch_ordered_collection[i])
                roll_outliers.append(roll_ordered_collection[i])
                yaw_outliers.append(yaw_ordered_collection[i])
            if y < (mean - std12):
                xout.append(x1[i])
                acc_z_outliers.append(acc_z_ordered_collection[i])
                acc_y_outliers.append(acc_y_ordered_collection[i])
                acc_x_outliers.append(acc_x_ordered_collection[i])
                pitch_outliers.append(pitch_ordered_collection[i])
                roll_outliers.append(roll_ordered_collection[i])
                yaw_outliers.append(yaw_ordered_collection[i])
            i += 1

        # RANDOMLY SAMPLE ALL DATA AND CLASSIFY

        sampleCount = 0
        sampled = []
        while sampleCount < (numberOfSamples - (numberOfSamples/3)):
            classifier = 0 #0 for undamaged 1 for damaged
            randIndex = random.randint(1, x1.__len__())

            attempts = 0
            while sampled.__contains__(randIndex):
                randIndex = random.randint(1, x1.__len__())
                if attempts > 10000:
                    break
                attempts += 1
            if attempts > 10000:
                break

            sampled.append(randIndex)
            if acc_z_ordered_collection[randIndex] > (mean + std12) or acc_z_ordered_collection[randIndex] < (mean - std12):
                classifier = 1
            dataEntry = [x1[randIndex], acc_z_ordered_collection[randIndex], acc_y_ordered_collection[randIndex], acc_x_ordered_collection[randIndex], pitch_ordered_collection[randIndex], roll_ordered_collection[randIndex], yaw_ordered_collection[randIndex], classifier]
            writer.writerow(dataEntry)
            sampleCount += 1

        # RANDOMLY SAMPLE OUTLIERS TO ENSURE ADEQUATE TESTING AND TRAINING DATA

        while sampleCount < numberOfSamples:
            classifier = 1
            randIndex = random.randint(1, xout.__len__())

            attempts = 0
            while sampled.__contains__(randIndex):
                randIndex = random.randint(1, xout.__len__())
                if attempts > 10000:
                    break
                attempts += 1
            if attempts > 10000:
                break

            sampled.append(randIndex)
            dataEntry = [xout[randIndex], acc_z_outliers[randIndex], acc_y_outliers[randIndex], acc_x_outliers[randIndex], pitch_outliers[randIndex], roll_outliers[randIndex], yaw_outliers[randIndex], classifier]
            writer.writerow(dataEntry)
            sampleCount += 1
