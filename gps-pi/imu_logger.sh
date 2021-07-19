#!/bin/bash

port="$1"
output="$2"

while true; do
    timestamp=`date +%Y%m%d%H%M%S`
    ./imu_logger.py \
        ${port} \
	${output} \
	1> ${output}/imu_stdout_${timestamp}.log \
	2> ${output}/imu_stderr_${timestamp}.log
done
