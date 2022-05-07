#!/bin/bash

port="$1"
output="$2"

while true; do
    timestamp=`date +%Y%m%d%H%M%S`
    ./gpsimu_logger.py \
        ${port} \
	${output} \
	1> ${output}/gpsimu_stdout_${timestamp}.log \
       	2> ${output}/gpsimu_stderr_${timestamp}.log
done
