import math
LOW_RANGE = range(120, 110, -1)
HIGH_RANGE = range(240, 250)

def process_scan(scan_data, data, ghost, period=3):
    for i in range(len(ghost)):
        ghost[i] -= 1
        if ghost[i] == 0:
            data[i] = 0
    for angle, distance in scan_data:
        i = round(angle) % 360
        data[i] = distance
        ghost[i] = period

def convert_to_xy(data, offset=0):
    new_data = [(0,0,0)] * len(data)
    for angle in range(len(data)):
        x = data[angle] * math.sin(math.radians(angle+offset))
        y = data[angle] * math.cos(math.radians(angle+offset))
        new_data[angle] = (data[angle], x, y)
    return new_data

def calc_gauge(data):
    min_dist_left = min_dist_right = 999999
    min_dist_left_i = min_dist_right_i = -1
    for i in LOW_RANGE:
        if data[i][0] <= min_dist_left and data[i][0] > 0:
            min_dist_left = data[i][0]
            min_dist_left_i = i
    for i in HIGH_RANGE:
        if data[i][0] <= min_dist_right and data[i][0] > 0:
            min_dist_right = data[i][0]
            min_dist_right_i = i

    if min_dist_right_i == -1 or min_dist_left_i == 0:
        return (0, 0, (0, 0), (0, 0))

    p1 = (data[min_dist_left_i][1], data[min_dist_left_i][2])
    p2 = (data[min_dist_right_i][1], data[min_dist_right_i][2])

    x = p1[0] - p2[0]
    y = p1[1] - p2[1]
    z = math.sqrt(x*x + y*y) / 25.4  # Convert to inches

    slope = math.degrees(math.atan(y / x))

    return (z, slope, p1,p2)
