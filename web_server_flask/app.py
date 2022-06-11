"""
UNH Capstone 2022 Project

Ben Grimes, Jeff Fernandes, Max Hennessey, Liqi Li
"""
from statistics import mean
from flask import Flask, render_template, request, abort, jsonify, redirect, send_file
import os
import io
import json
import data_to_range
import track_data_stats
import my_db

DATABASE = "TrackDataDB.db"

app = Flask(__name__)

currentPath = ''


def json_to_json_array(in_file):
    file_in = open(in_file, "r")

    lines = file_in.readlines()
    data = '{"jsonarray" :['

    for line in lines:
        data += (line.strip('\n') + "," + "\n")

    data = data.rstrip()[:-1]
    data += "]}"
    file_in.close()
    jData = json.dumps(data)
    return data


@app.before_first_request
def initialize():
    my_db.init_db()
    # data = my_db.get_data(6, 7)
    # for row in data:
    #     acc_z, mileage = row
    #     print(acc_z)
    #     print(str(mileage) + " = Mileage")


@app.route('/', methods=['POST', 'GET'])
def main_page():
    if request.method == 'POST':
        minRange = request.form['minRange']
        maxRange = request.form['maxRange']
        print(minRange, maxRange)

        data = my_db.get_data(minRange, maxRange)
        acc_z_list = []
        mileage_list = []

        for row in data:
            acc_z, mileage = row
            acc_z_list.append(acc_z)
            mileage_list.append(mileage)

        stats_rows = my_db.get_stats(minRange, maxRange)
        stat_x_list = []
        stat_y_list = []
        stat_z_list = []
        stat_r_list = []
        stat_p_list = []
        stat_ya_list = []

        stats_list = []

        for obj in stats_rows:
            stat_x, stat_y, stat_z, stat_r, stat_p, stat_ya = obj
            stat_x_list.append(stat_x)
            stat_y_list.append(stat_y)
            stat_z_list.append(stat_z)
            stat_r_list.append(stat_r)
            stat_p_list.append(stat_p)
            stat_ya_list.append(stat_ya)

        stats_list.append(mean(stat_x_list))
        stats_list.append(mean(stat_y_list))
        stats_list.append(mean(stat_z_list))
        stats_list.append(mean(stat_r_list))
        stats_list.append(mean(stat_p_list))
        stats_list.append(mean(stat_ya_list))

        print(stats_list)

        stats_names = ['acc_x', 'acc_y', 'acc_z', 'roll', 'pitch', 'yaw']

        return render_template('index.html', minRange=minRange, maxRange=maxRange,
                               acc_z=acc_z_list, mileage=mileage_list, stats_names=stats_names,
                               stats_list=stats_list)
    else:
        return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/info')
def info():
    return render_template('info.html')


@app.route('/stats')
def display_stats():
    # TODO get location passed as argument
    location = request.args.get('location')
    print(location)
    track_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    # TODO add location to all paths
    if os.path.isfile('data/wolfeboro/stats/stats.json'):
        return render_template("stats.html", track_data=track_data)
    track_data_stats.write_average_json_file(currentPath, 'data/wolfeboro/stats/stats.json')
    track_data_stats.write_std_json_file(currentPath, 'data/wolfeboro/stats/stats.json')
    return render_template("stats.html", track_data=track_data)


@app.route('/chart', methods=['POST', 'GET'])
def display_chart_from_location_range():
    print(request.method)
    if request.method == 'POST':
        print(request.method)
        location = request.args.get('location')
        minRange = request.args.get('minRange')
        maxRange = request.args.get('maxRange')

        data = my_db.get_data(minRange, maxRange)
        acc_z_list = []
        mileage_list = []
        for row in data:
            acc_z, mileage = row
            acc_z_list.append(acc_z)
            mileage_list.append(mileage)

        print(acc_z_list)

        return render_template('chart.html', location=location, minRange=minRange, maxRange=maxRange,
                               acc_z=acc_z_list, mileage=mileage_list)
    else:
        print(request.method)
        return render_template('chart.html')


@app.route('/chart_data/<location>', methods=['GET'])
def chart_data(location):
    path = get_json_file(location)

@app.route('/slideShow/<imagefile>', methods=['GET'])
def read_image(imagefile):
    return send_file("slideShow/"+imagefile, mimetype='image/jpeg')

def get_json_file(location, minRange=None, maxRange=None):
    path = None
    global currentPath
    if location is not None:
        path = "data/" + str(location)
        if os.path.isdir(path) is False:
            path = None
            currentPath = path
            return path
    else:
        currentPath = path
        print(currentPath)
        return path
    ## path == data/{some location directory}
    if minRange is not None and maxRange is not None:
        rangePath = path + "/" + str(location) + "_" + str(minRange) + "_" + str(maxRange) + ".json"
        if os.path.isfile(rangePath) is True:
            currentPath = rangePath
            return rangePath
        else:
            data_to_range.write_json_data_to_range(rangePath, path + "/" + str(location) + ".json", minRange, maxRange)
            currentPath = rangePath
            return rangePath
    else:
        path += str(location) + ".json"
    currentPath = path
    return path


if __name__ == '__main__':
    app.run(debug=True)
