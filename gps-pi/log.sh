#!/bin/bash

cd `dirname $0`

mount /dev/sda1 /media/usb0

if [ -d /media/usb0/PIRAIL ]; then
  output=/media/usb0/PIRAIL/`date +%Y%m%d`
else
  output=/root/gps-data
fi

mkdir -p ${output}

while true; do
  timestamp=`date +%Y%m%d%H%M`
  ./combolog9.py ${output} \
    >> ${output}/${timestamp}_stdout.txt \
    2>> ${output}/${timestamp}_stderr.txt
done
