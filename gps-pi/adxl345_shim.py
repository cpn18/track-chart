#import the adxl345 module
import adxl345

#create ADXL345 object
accel = adxl345.ADXL345()


def get_axes():
      #get axes as g
      #axes = accel.getAxes(True)

      # to get axes as ms^2 use
      axes = accel.getAxes(False)

      return {'x': axes['x'], 'y': axes['y'], 'z': axes['z']}

