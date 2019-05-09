#!/bin/bash

output=/root/gps-data

cd `dirname $0`

mkdir -p ${output}

if [ -f ${output}/error.log ]; then
  mv ${output}/error.log ${output}/error.log.0
fi

while true; do
  date +%Y%m%d%H%M > ${output}/timestamp
  ./combolog5_web.py \
	  >> ${output}/`cat ${output}/timestamp`_log.csv \
	  2>> ${output}/error.log
done
