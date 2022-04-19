import os
import sys
import _collections
from desktop import track_data
from desktop.acceleration_gyroscopic_data import acceleration_gyroscopic_data


def main():
    # Assure the items in dictionary are sorted by mileage with OrderedDict
    track_d = _collections.OrderedDict(sorted(
        track_data.json_to_dict_mileage("data/wrr_20211023_with_mileage_sort_by_time.json",
                                        "../known/wolfeboro.csv").items()))
    track_d_range_4_6 = _collections.OrderedDict(sorted(track_data.select_range(track_d, 4, 6).items()))

    ## Ranges that are out of bounds raise an exception
    # track_d_range_20_30 = _collections.OrderedDict(sorted(track_data.select_range(track_d, 20,30).items()))

    averages: acceleration_gyroscopic_data = track_data.calc_average_acceleration_gyro(track_d_range_4_6)
    print("Averages: \n\t Acc[X,Y,Z]: {}\n\t Gyro[X,Y,Z]: {}".format(averages.get_acceleration_cartesian(),
                                                                     averages.get_gyro_cartesian()))

    standard_deviation: acceleration_gyroscopic_data = track_data.calc_standard_deviation_all(track_d_range_4_6)
    print(
        "Standard Deviation: \n\t Acc[X,Y,Z]: {}\n\t Gyro[X,Y,Z]: {} ".format(
            standard_deviation.get_acceleration_cartesian() , standard_deviation.get_gyro_cartesian()
        ))

    min_all: acceleration_gyroscopic_data = track_data.get_minAll(track_d_range_4_6)
    print(
        "Minimum: \n\t Acc[X,Y,Z]: {}\n\t Gyro[X,Y,Z]: {}".format(
                min_all.get_acceleration_cartesian() , min_all.get_gyro_cartesian()
            ))

    max_all: acceleration_gyroscopic_data = track_data.get_maxAll(track_d_range_4_6)
    print(
        "Maximum: \n\t Acc[X,Y,Z]: {}\n\t Gyro[X,Y,Z]: {}".format(
                max_all.get_acceleration_cartesian() , max_all.get_gyro_cartesian()
            ))

    xOutliers = track_data.getOutlierX(track_d_range_4_6)
    print("Outliers for X axis:")
    for x in xOutliers:
        print(x)

    yOutliers = track_data.getOutlierY(track_d_range_4_6)
    print("Outliers for Y axis:")
    for x in yOutliers:
        print(x)

    zOutliers = track_data.getOutlierZ(track_d_range_4_6)
    print("Outliers for Z axis:")
    for x in zOutliers:
        print(x)

    rollOutliers = track_data.getOutlierRoll(track_d_range_4_6)
    print("Outliers for Roll axis:")
    for x in rollOutliers:
        print(x)

    pitchOutliers = track_data.getOutlierPitch(track_d_range_4_6)
    print("Outliers for Pitch axis:")
    for x in pitchOutliers:
        print(x)

    yawOutliers = track_data.getOutlierYaw(track_d_range_4_6)
    print("Outliers for Yaw axis:")
    for x in yawOutliers:
        print(x)



if __name__ == "__main__":
    main()
