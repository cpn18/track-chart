#!/bin/bash

config="config.json"
usb_drive="/dev/sda1"
mount_point="/media/usb0"
pirail_data=${mount_point}/PIRAIL

cd `dirname $0`

if [ -b ${usb_drive} ]; then
  if [ ! -d ${mount_point} ]; then
    mkdir -p ${mount_point}
  fi

  mount ${usb_drive} ${mount_point}
fi

./wait_for_gps_fix.py

if [ -d ${pirail_data} ]; then
  output=${pirail_data}/`date +%Y%m%d`
else
  output=/root/gps-data
fi

mkdir -p ${output}

if [ ! -f ${config} ]; then
  cp ${config}.sample ${config}
fi

./launcher.py ${output}
