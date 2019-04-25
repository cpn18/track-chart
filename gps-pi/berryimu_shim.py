#import the Berry IMU module
import IMU 

IMU.detectIMU()
IMU.initIMU()

#lsb = 0.061/1000.0 # 2
#lsb = 0.122/1000.0 # 4
lsb = 0.244/1000.0 # 8
#lsb = 0.732/1000.0 # 16 

lsb *= 9.80665

def get_axes():
    return {
        'x': lsb*IMU.readACCx(),
        'y': lsb*IMU.readACCy(),
        'z': lsb*IMU.readACCz(),
    }
