#!/bin/bash

port="$1"
output="$2"

while true; do
    timestamp=`date +%Y%m%d%H%M%S`
    ./lidar_logger.py \
        ${port} \
	${output} \
	1> ${output}/lidar_stdout_${timestamp}.log \
       	2> ${output}/lidar_stderr_${timestamp}.log
done
