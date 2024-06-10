import pirail

import plot_3dlidar_from_json

#SOURCE="/run/media/jminer/8808-4BCF/PIRAIL/20240424/202404241832_lidar.json"
#SOURCE="/run/media/jminer/8808-4BCF/PIRAIL/20240422/202404220217_lidar.json"
SOURCE="/run/media/jminer/8808-4BCF/PIRAIL/20240421/202404212048_lidar.json"

def invalid_depth(depth):
    return depth in [0x0000, 0xFF14, 0xFF78, 0xFFDC, 0xFFFA]

def find_neighbors(obj, row1, col1):
    neighbors = []
    d1 = obj['depth'][row1][col1]
    for row2 in range(len(obj['depth'])):
        for col2 in range(len(obj['depth'][row1])):
            if row1 != row2 and col1 != col2:
                d2 = obj['depth'][row2][col2]

                v = (row2-row1)**2 + (col2-col1)**2 + (d2-d1)**2

                if v <= 1000:
                    neighbors.append((row2,col2))
    return neighbors

def find_min_max(obj):
    maxd = 0
    mind = 9999
    maxc = 0
    for row in range(len(obj['depth'])):
        for col in range(len(obj['depth'][row])):
            v = obj['depth'][row][col]
            if not invalid_depth(v):
                if v > maxd:
                    maxd = v
                    maxp = (row, col)
                if v < mind:
                    mind = v
                    minp = (row, col)
    return [mind, minp, maxd, maxp]

def process_frame(obj, slice_number):

    mind, minp, maxd, maxp = find_min_max(obj)
    #print("min", mind, minp)
    #print("max", maxd, maxp)

    def search_all():
        maxc = 0
        for row in range(len(obj['depth'])):
            for col in range(len(obj['depth'][row])):
                v = obj['depth'][row][col]
                if not invalid_depth(v):
                    neighbors = find_neighbors(obj, row, col)
                    count = len(neighbors)
                    if count > maxc:
                        #print((row, col), count, neighbors)
                        maxc = count
                        maxcpos = neighbors
                        maxcpos.append((row, col))
        #print("maxc", maxc, maxcpos)
        return maxcpos

    def search_one(row, col):
        neighbors = find_neighbors(obj, row, col)
        neighbors.append((row, col))
        return neighbors

    # Really slow... detects biggest
    #neighbors = search_all()

    # Closest
    neighbors = search_one(minp[0], minp[1])

    plot_3dlidar_from_json.plot(obj['depth'], slice_number, neighbors)
    #plot_3dlidar_from_json.plot(obj['depth'], 1)


slice_number = 1
for line,obj in pirail.read(SOURCE, classes=["LIDAR3D"]):
    if 'depth' in obj:
        process_frame(obj, slice_number) 
        slice_number += 1
        print(slice_number)
