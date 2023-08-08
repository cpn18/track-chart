#!/bin/bash

port="$1"
output="$2"

while true; do
    timestamp=`date +%Y%m%d%H%M%S`
    ./hps_lidar_logger.py \
        ${port} \
	${output} \
	1> ${output}/hps_lidar_stdout_${timestamp}.log \
       	2> ${output}/hps_lidar_stderr_${timestamp}.log
done
