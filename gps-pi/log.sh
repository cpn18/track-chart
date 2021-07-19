#!/bin/bash

cd `dirname $0`

mount /dev/sda1 /media/usb0

./wait_for_gps_fix.py

if [ -d /media/usb0/PIRAIL ]; then
  output=/media/usb0/PIRAIL/`date +%Y%m%d`
else
  output=/root/gps-data
fi

mkdir -p ${output}

./web_server.sh 80 ${output} &
./gps_logger.sh 8080 ${output} &
./imu_logger.sh 8081 ${output} &
