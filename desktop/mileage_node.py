from desktop import acceleration_gyroscopic_data

class mileage_node(object):

    def __init__(self, mileage, data: acceleration_gyroscopic_data.acceleration_gyroscopic_data, left=None, right=None):
        self.mileage = mileage
        self.data: acceleration_gyroscopic_data.acceleration_gyroscopic_data = data
        self.left = left
        self.right = right
        self.height = 1