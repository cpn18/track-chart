#!/bin/bash

hash=$(git describe --tags)

files="adxl345.py \
    adxl345_shim.py \
    berryimu_shim.py \
    config.json.sample \
    geo.py \
    gps_logger.py \
    gps_logger.sh \
    imu_logger.py \
    imu_logger.sh \
    IMU.py \
    launcher.py \
    lidar_logger.py \
    lidar_logger.sh \
    hps_lidar_logger.py \
    hps_lidar_logger.sh \
    hps_3d_160_lidar.py \
    crc16.py \
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
    util.py \
    htdocs \
    js \
    os_setup"

echo $hash > version.txt
file=${HOME}/PiRail-${hash}.tgz
cp ../desktop/geo.py .
tar -zcf ${file} ${files} version.txt
rm version.txt geo.py
echo "Wrote ${file}"
