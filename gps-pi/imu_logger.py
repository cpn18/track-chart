import time
import math
import datetime
import json
import os
import berryimu_shim as accel

AA = 0.98

MAX_MAG_X = -7
MIN_MAG_X = -1525
MAX_MAG_Y = 1392
MIN_MAG_Y = 277
MAX_MAG_Z = -1045
MIN_MAG_Z = -1534

# Insert delay if Exception occurs
ERROR_DELAY = 1

# Loop delay
LOOP_DELAY = 0.02

# Version
VERSION = 9

# Set to True to exit
DONE = False

def _get_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as t:
        return float(t.read())/1000

def imu_logger(output_directory):
    """ IMU Logger """
    gyroXangle = gyroYangle = gyroZangle = 0
    CFangleX = CFangleY = CFangleZ = 0

    # Configure Axis
    try:
        with open("config.json", "r") as f:
            config = json.loads(f.read())
    except:
        config = {"class": "CONFIG", "imu": {"log": True, "x": "x", "y": "y", "z": "z"}}
    config['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Create the output directory
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    # Open the output file
    with open(os.path.join(output_directory,datetime.datetime.now().strftime("%Y%m%d%H%M")+"_imu.csv"), "w") as imu_output:
        imu_output.write("#v%d\n" % VERSION)
        imu_output.write("%s %s %s *\n" % (config['time'], config['class'], json.dumps(config)))

        now = time.time()
        while not DONE:
             last_time = now
             now = time.time()
             acc = accel.get_axes()

             # Calibration
             acc['MAGx'] -= (MAX_MAG_X + MIN_MAG_X) / 2
             acc['MAGy'] -= (MAX_MAG_Y + MIN_MAG_Y) / 2
             acc['MAGz'] -= (MAX_MAG_Z + MIN_MAG_Z) / 2

             obj = {
                 "class": "ATT",
                 "device": accel.device(),
                 "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                 "acc_x": acc['ACC'+config['imu']['x']],
                 "acc_y": acc['ACC'+config['imu']['y']],
                 "acc_z": acc['ACC'+config['imu']['z']],
                 "gyro_x": acc['GYR'+config['imu']['x']],
                 "gyro_y": acc['GYR'+config['imu']['y']],
                 "gyro_z": acc['GYR'+config['imu']['z']],
                 "mag_x": acc['MAG'+config['imu']['x']],
                 "mag_y": acc['MAG'+config['imu']['y']],
                 "mag_z": acc['MAG'+config['imu']['z']],
                 "temp": _get_temp(),
             }

             DT = now - last_time

             # Calculate Angle From Gyro
             #gyroXangle += acc['GYRx'] * DT
             #gyroYangle += acc['GYRy'] * DT
             #gyroZangle += acc['GYRz'] * DT

             # Calculate Yaw, Pitch and Roll with data fusion
             AccXangle = math.degrees(math.atan2(obj['acc_y'], obj['acc_z']))
             AccYangle = math.degrees(math.atan2(obj['acc_z'], obj['acc_x']))
             AccZangle = math.degrees(math.atan2(obj['acc_x'], obj['acc_y']))

             CFangleX = AA*(CFangleX+obj['gyro_x']*DT) + (1-AA)*AccXangle
             CFangleY = AA*(CFangleY+obj['gyro_y']*DT) + (1-AA)*AccYangle
             CFangleZ = AA*(CFangleZ+obj['gyro_z']*DT) + (1-AA)*AccZangle

             obj['pitch'] = CFangleX
             obj['pitch_st'] = "N"
             obj['roll'] = CFangleY - 90
             obj['roll_st'] = "N"
             obj['yaw'] = CFangleZ
             obj['yaw_st'] = "N"

             # Calculate Heading
             obj['heading'] = (math.degrees(math.atan2(obj['mag_y'], obj['mag_x'])) - 90) % 360.0

             # Calculate vector length
             obj["acc_len"] = math.sqrt(obj['acc_x']**2+obj['acc_y']**2+obj['acc_z']**2)
             obj["mag_len"] = math.sqrt(obj['mag_x']**2+obj['mag_y']**2+obj['mag_z']**2)
             obj["mag_st"] = "N"

             # Log the output
             imu_output.write("%s %s %s *\n" % (obj['time'], obj['class'], json.dumps(obj)))

             #print(json.dumps(obj))
             #print("AccLen %7.3f\tYaw %7.3f\tPitch %7.3f\tRoll %7.3f" % (obj['acc_len'],obj['yaw'], obj['pitch'], obj['roll']))
             #print("MagLen %7.3f\tMagX %d\tMagY %d\tMagZ %d\tMagHeading %7.3f" % (obj['mag_len'], obj['mag_x'], obj['mag_y'], obj['mag_z'], obj['heading']))

             # Delay Loop
             while (time.time() - now) < LOOP_DELAY:
                 time.sleep(LOOP_DELAY/2)

if __name__ == "__main__":
    print("Press <Ctrl-C> to exit")
    while not DONE:
        try:
            imu_logger(datetime.datetime.now().strftime("%Y%m%d"))
        except KeyboardInterrupt:
            DONE = True
        except Exception as ex:
            print("IMU Exception: %s" % ex)
            time.sleep(ERROR_DELAY)
    print("Exiting...")
