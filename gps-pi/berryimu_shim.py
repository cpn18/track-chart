#import the Berry IMU module
import IMU 

IMU.detectIMU()
IMU.initIMU()

ONE_G = 9.80665

#ACC_LSB = ONE_G * 0.061/1000.0 # 2
#ACC_LSB = ONE_G * 0.122/1000.0 # 4
ACC_LSB = ONE_G * 0.244/1000.0 # 8
#ACC_LSB = ONE_G * 0.732/1000.0 # 16 

GYRO_GAIN = 0.070


def device():
    return "LSM9DS1"

def get_axes():
    return {
        'ACCx': IMU.readACCx() * ACC_LSB,
        'ACCy': IMU.readACCy() * ACC_LSB,
        'ACCz': IMU.readACCz() * ACC_LSB,
        'GYRx': IMU.readGYRx() * GYRO_GAIN,
        'GYRy': IMU.readGYRy() * GYRO_GAIN,
        'GYRz': IMU.readGYRz() * GYRO_GAIN,
        'MAGx': IMU.readMAGx(),
        'MAGy': IMU.readMAGy(),
        'MAGz': IMU.readMAGz(),
    }
