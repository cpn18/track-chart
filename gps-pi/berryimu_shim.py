#import the Berry IMU module
import IMU 

IMU.detectIMU()
IMU.initIMU()

#lsb = 0.061/1000.0 # 2
#lsb = 0.122/1000.0 # 4
lsb = 0.244/1000.0 # 8
#lsb = 0.732/1000.0 # 16 

g_gain = 0.070

lsb *= 9.80665

def device():
    return "LSM9DS1"

def get_axes():
    return {
        'ACCx': lsb*IMU.readACCx(),
        'ACCy': lsb*IMU.readACCy(),
        'ACCz': lsb*IMU.readACCz(),
        'GYRx': g_gain*IMU.readGYRx(),
        'GYRy': g_gain*IMU.readGYRy(),
        'GYRz': g_gain*IMU.readGYRz(),
    }
