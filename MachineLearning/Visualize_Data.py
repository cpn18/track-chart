"""
UNH Capstone 2022 Project

Ben Grimes, Jeff Fernandes, Max Hennessey, Liqi Li
"""
import json
import numpy as np
import seaborn as sn
import pandas as panda
import matplotlib.pyplot as plt

def create_graph_for_select_axis(pathToFile1, axis):
    file_in1 = open(pathToFile1, "r")

    lines1 = file_in1.readlines()

    xl1 = []
    yl1 = []

    #print("Reading")

    for line in lines1:
        d = {}
        d = json.loads(line)
        if 'mileage' in d and axis in d:
            xl1.append(d['mileage'])
            yl1.append( d[axis])

    file_in1.close()



    x1 = np.asarray(xl1)
    y1 = np.asarray(yl1)
    mean = np.mean(y1)
    #Highlight Different Standard Deviations
    std = np.std(y1)
    std2 = std * 2.0
    std4 = std * 4.0
    std8 = std * 8.0
    std16 = std * 16.0
    xout = []
    yout = []

    i = 0
    for y in yl1:
        if y > (mean + std8):
            xout.append(x1[i])
            yout.append(y1[i])
        if y < (mean - std8):
            xout.append(x1[i])
            yout.append(y1[i])
        i += 1


    plt.title("PiRail")
    plt.xlabel("Mileage")
    plt.ylabel(axis)

    plt.scatter(x1, y1, s=2, c='gray', alpha=.25)

    plt.scatter(xout, yout, s=10, c='r', alpha=.5, marker='x')
    plt.axhline(y=mean + std, color='g', linestyle='-')
    plt.axhline(y=mean - std, color='g', linestyle='-')
    plt.axhline(y=mean + std2, color='b', linestyle='-')
    plt.axhline(y=mean - std2, color='b', linestyle='-')
    plt.axhline(y=mean + std4, color='orange', linestyle='-')
    plt.axhline(y=mean - std4, color='orange', linestyle='-')
    plt.axhline(y=mean + std8, color='y', linestyle='-')
    plt.axhline(y=mean - std8, color='y', linestyle='-')
    plt.axhline(y=mean + std16, color='y', alpha=.25, linestyle='-')
    plt.axhline(y=mean - std16, color='y', alpha=.25, linestyle='-')
    plt.axhline(y=mean, color='r', linestyle='-')
    plt.xticks(np.arange(min(x1), max(x1)+1, .5))
    plt.yticks(np.arange(min(y1), max(y1)+1, std))

    plt.legend()

    plt.show()

def graph_correlation_axis(pathToFile1, axis1, axis2):
    file_in1 = open(pathToFile1, "r")

    lines1 = file_in1.readlines()

    xl1 = []
    yl1 = []

    i = 0
    for line in lines1:
        d = json.loads(line)

        if axis1 in d and axis2 in d:
            xl1.append(d[axis1])
            yl1.append(d[axis2])
            i += 1

    file_in1.close()

    x1 = np.asarray(xl1)
    y1 = np.asarray(yl1)

    ybar = np.mean(y1)
    xbar = np.mean(x1)

    b1 = 0
    nb1 = 0
    den1 = 0
    den2 = 0
    den3 = 0

    for i in range(0, x1.__len__()):
        nb1 += (x1[i] - xbar) * (y1[i] - ybar)
        den1 += pow((x1[i] - xbar), 2)
        den3 += pow((y1[i] - ybar), 2)

    den2 = den1 ** 2
    den3 = den3 ** 2
    den4 = den3 * den2
    corrXY = nb1 / den4


    b1 = nb1/ den1
    b0 = ybar - (b1 * xbar)


    plt.title("Correlation of: "+axis1 +", "+axis2+": "+corrXY.__str__())
    plt.xlabel(axis1)
    plt.ylabel(axis2)

    plt.scatter(x1, y1, s=2, c='green', edgecolors='black', linewidths=1, alpha=.75)
    plt.plot(x1, b1*x1+b0, '-r')

    plt.show()

def visualize_generated_data():
    df_train = panda.read_csv("training.csv")# generated data

    matrix = df_train.corr()
    sn.heatmap(matrix, annot=True)
    plt.show()
    ax = sn.countplot(x='damaged', data=df_train)
    plt.show()
