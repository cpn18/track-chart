"""
IMU SHIM for the ADXL345
"""
import adxl345

#create ADXL345 object
accel = adxl345.ADXL345()

def device():
    """ Return Device Name """
    return "ADXL345"

def get_axes():
    """ Read the Axes """

    # to get axes as ms^2 use
    axes = accel.getAxes(False)

    return {
       'ACCx': axes['x'],
       'ACCy': axes['y'],
       'ACCz': axes['z'],
       'GYRx': 0, 
       'GYRy': 0, 
       'GYRz': 0, 
       'MAGx': 0, 
       'MAGy': 0, 
       'MAGz': 0, 
    }

