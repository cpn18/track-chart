#!/bin/bash

config="config.json"

cd `dirname $0`

mount /dev/sda1 /media/usb0

./wait_for_gps_fix.py

if [ -d /media/usb0/PIRAIL ]; then
  output=/media/usb0/PIRAIL/`date +%Y%m%d`
else
  output=/root/gps-data
fi

mkdir -p ${output}

if [ ! -f ${config} ]; then
  cp ${config}.sample ${config}
fi

./launcher.py ${output}
