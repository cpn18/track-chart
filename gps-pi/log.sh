#!/bin/bash

output=/root/gps-data

cd `dirname $0`

mkdir -p ${output}

if [ -f ${output}/error.log ]; then
  mv ${output}/error.log ${output}/error.log.0
fi

mii-tool eth0 >> ${output}/error.log

#if [ "`mii-tool eth0`" == "eth0: no link" ]; then
  ./audio_capture.sh &
  while true; do
    date +%Y%m%d%H%M > ${output}/timestamp
    ./combolog9.py \
	    >> ${output}/`cat ${output}/timestamp`_log.csv \
	    2>> ${output}/error.log
  done
#fi
