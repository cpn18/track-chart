#!/bin/bash

hash=$(git describe --tags)

files="adxl345.py \
    adxl345_shim.py \
    berryimu_shim.py \
    config.json.sample \
    gps_logger.py \
    gps_logger.sh \
    imu_logger.py \
    imu_logger.sh \
    IMU.py \
    launcher.py \
    lidar_logger.py \
    lidar_logger.sh \
    log.sh \
    lpcm_collect.sh \
    lpcm_logger.py \
    lpcm_logger.sh \
    LSM9DS0.py \
    LSM9DS1.py \
    nmea.py \
    pirail-mini.py \
    wait_for_gps_fix.py \
    web_server.py \
    web_server.sh \
    htdocs \
    js \
    os_setup"

echo $hash > version.txt
file=${HOME}/PiRail-${hash}.tgz
tar -zcf ${file} ${files} version.txt
rm version.txt
echo "Wrote ${file}"
