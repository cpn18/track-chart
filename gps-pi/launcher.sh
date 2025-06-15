#!/bin/bash

config="config.json"
usb_drive="/dev/sda1"
mount_point="/media/usb0"
pirail_data=${mount_point}/PIRAIL

cd `dirname $0`

# Try to mount the USB drive
if [ -b ${usb_drive} ]; then
  if [ ! -d ${mount_point} ]; then
    mkdir -p ${mount_point}
  fi

  mount ${usb_drive} ${mount_point}
fi

# If the PiRail Data directory is found, use it
if [ -d ${pirail_data} ]; then
  output=${pirail_data}
else
  output=${HOME}/gps-data
fi

# Add a date stamp
output=${output}/`date +%Y%m%d`

# Create the directory if needed
mkdir -p ${output}

# If the configuration file doesn't exist, copy the sample
if [ ! -f ${config} ]; then
  cp ${config}.sample ${config}
fi

# Wait for a GPS fix... this can be troublesome with poor GPS coverage
./wait_for_gps_fix.py

# Launch everything else
./launcher.py ${output}
