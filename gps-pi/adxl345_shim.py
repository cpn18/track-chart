#import the adxl345 module
import adxl345

#create ADXL345 object
accel = adxl345.ADXL345()


def get_axes():
      #get axes as g
      #axes = accel.getAxes(True)

      # to get axes as ms^2 use
      axes = accel.getAxes(False)

      return {
         'ACCx': axes['x'],
         'ACCy': axes['y'],
         'ACCz': axes['z'],
         'GYRx': 0, 
         'GYRy': 0, 
         'GYRz': 0, 
      }

