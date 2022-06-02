"""
UNH Capstone 2022 Project

Ben Grimes, Jeff Fernandes, Max Hennessey, Liqi Li
"""

class acceleration_gyroscopic_data:

    def __init__(self, accX, accY, accZ, roll, pitch, yaw):
        self.accX = accX
        self.accY = accY
        self.accZ = accZ
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

    def get_acceleration_cartesian(self):
        return [self.accX, self.accY, self.accZ]

    def get_gyro_cartesian(self):
        return [self.roll, self.pitch, self.yaw]

    def get_accX(self):
        return self.accX

    def get_accY(self):
        return self.accY

    def get_accZ(self):
        return self.accZ

    def get_roll(self):
        return self.roll

    def get_pitch(self):
        return self.pitch

    def get_yaw(self):
        return self.yaw
